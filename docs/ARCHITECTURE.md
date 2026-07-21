# Архитектура Kubernetes-стенда

## 1. Общая схема

Кластер состоит из трёх виртуальных машин Ubuntu:

| Узел | Роль | Внутренний IP |
|---|---|---|
| kube1 | control-plane, NFS server | 192.168.56.11 |
| kube2 | worker | 192.168.56.12 |
| kube3 | worker | 192.168.56.13 |

Кластер создан с помощью kubeadm.

Container runtime: containerd.

Сетевой плагин: Calico.

Внутренняя Pod-сеть:

10.244.0.0/16

## 2. Сетевые интерфейсы VMware

Используются две виртуальные сети.

### VMnet8 NAT

Используется для доступа виртуальных машин во внешнюю сеть и для административного SSH-доступа.

### VMnet2 Host-only

Сеть:

192.168.56.0/24

Используется для постоянного взаимодействия Kubernetes-узлов.

Статические адреса:

- kube1 — 192.168.56.11
- kube2 — 192.168.56.12
- kube3 — 192.168.56.13

Kubernetes использует именно эти адреса как InternalIP узлов.

## 3. Архитектура приложения

Пользовательский запрос проходит по цепочке:

Client
– Ingress NGINX
– frontend Service
– frontend Pods
– backend Service
– backend Pods
– PostgreSQL Service
– postgres-0
– PersistentVolume
– NFS server

## 4. Прикладные компоненты

### Frontend

Deployment с двумя репликами.

Образ:

frontend:v1

Service:

ClusterIP

### Backend

Deployment с тремя репликами.

Используемые версии:

- backend:v1
- backend:v2

Версия v2 используется для эксперимента RollingUpdate.

### PostgreSQL

PostgreSQL запускается как StatefulSet.

Количество реплик базовой реализации:

1

Pod:

postgres-0

Данные сохраняются на PersistentVolume через NFS CSI.

## 5. Постоянное хранилище

NFS server расположен на kube1.

Export:

/srv/nfs/k8s

StorageClass:

nfs-csi

CSI provisioner:

nfs.csi.k8s.io

Цепочка хранения:

StatefulSet
– PVC
– StorageClass
– PV
– NFS CSI
– /srv/nfs/k8s

## 6. Сетевой доступ

Внешний запрос принимается Ingress Controller.

Ingress host:

kube-lab.local

Ingress направляет пользовательский трафик во frontend.

Frontend обращается к backend через Kubernetes Service.

Backend обращается к PostgreSQL через сервисное имя внутри Kubernetes.

## 7. Безопасность

В проекте используются:

- requests и limits;
- startupProbe;
- readinessProbe;
- livenessProbe;
- runAsNonRoot;
- allowPrivilegeEscalation: false;
- drop ALL capabilities;
- ServiceAccount;
- RBAC;
- NetworkPolicy;
- Kubernetes Secret для пароля БД.

Реальный пароль базы данных не хранится в Git.

## 8. NetworkPolicy

Реализована модель default deny.

Разрешаются только необходимые потоки:

Ingress – frontend

frontend – backend

backend – PostgreSQL

Pods – CoreDNS

## 9. Эксплуатационные эксперименты

В стенде проверяются:

1. Self-healing.
2. RollingUpdate v1 – v2.
3. Rollback.
4. Сохранность PostgreSQL.
5. Ошибочный Service selector и EndpointSlice.
6. Running != Ready.
7. NetworkPolicy и DNS.
8. cordon/drain worker-узла.
