# Развёртывание Kubernetes-кластера

## 1. Подготовка узлов

На всех трёх Ubuntu-узлах выполняется:

- настройка уникальных hostname;
- настройка статических адресов внутренней сети;
- отключение swap;
- загрузка необходимых kernel modules;
- настройка sysctl;
- установка containerd;
- установка kubeadm, kubelet и kubectl.

## 2. Сетевые адреса

Control plane:

192.168.56.11

Workers:

192.168.56.12
192.168.56.13

Pod CIDR:

10.244.0.0/16

## 3. Инициализация control-plane

Кластер создавался командой вида:

sudo kubeadm init \
  --kubernetes-version=v1.33.13 \
  --apiserver-advertise-address=192.168.56.11 \
  --pod-network-cidr=10.244.0.0/16 \
  --cri-socket=unix:///run/containerd/containerd.sock \
  --node-name=kube1

Параметр apiserver-advertise-address указывает постоянный адрес control-plane во внутренней сети VMware.

Pod network CIDR должен соответствовать конфигурации CNI.

## 4. kubeconfig

После kubeadm init административный kubeconfig копируется пользователю:

mkdir -p $HOME/.kube

sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config

sudo chown $(id -u):$(id -g) $HOME/.kube/config

## 5. Присоединение worker

Worker-узлы присоединяются через kubeadm join.

Для корректного выбора InternalIP используется явный node-ip:

kube2:

192.168.56.12

kube3:

192.168.56.13

## 6. Calico

Calico используется как CNI.

Pod CIDR:

10.244.0.0/16

Для автоматического выбора Kubernetes-интерфейса используется сеть:

192.168.56.0/24

Это предотвращает выбор NAT-интерфейса VMnet8 вместо внутреннего VMnet2.

## 7. Проверка кластера

Основная проверка:

kubectl get nodes -o wide

Ожидается:

kube1 Ready
kube2 Ready
kube3 Ready

Дополнительно проверяются:

- CoreDNS;
- Calico;
- межузловой Pod-to-Pod трафик;
- DNS внутри кластера.

# NFS и постоянное хранилище

## 8. NFS server

NFS server расположен на kube1.

Каталог:

/srv/nfs/k8s

Export разрешён для:

192.168.56.0/24

## 9. NFS CSI

Используется Kubernetes CSI driver:

csi-driver-nfs

Компоненты:

- csi-nfs-controller;
- csi-nfs-node на каждом узле.

## 10. StorageClass

Provisioner:

nfs.csi.k8s.io

NFS server:

192.168.56.11

Share:

/srv/nfs/k8s

ReclaimPolicy:

Retain

## 11. Проверка storage

kubectl get storageclass

kubectl get pvc -n homework

kubectl get pv

PVC PostgreSQL должен находиться в состоянии:

Bound

Удаление Pod postgres-0 не должно удалять данные на PersistentVolume.
