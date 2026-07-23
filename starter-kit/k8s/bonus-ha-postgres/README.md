# HA PostgreSQL bonus

This bonus demonstrates a real highly available PostgreSQL cluster
managed by CloudNativePG.

Architecture:

- 3 PostgreSQL instances
- 1 Primary
- 2 Standby replicas
- streaming replication
- dedicated persistent storage
- automatic failover
- automatic read-write service redirection

Failover test:

1. Create test data on Primary.
2. Delete the current Primary Pod.
3. Observe automatic promotion of a standby.
4. Verify the old data on the new Primary.
5. Insert new data after failover.
6. Verify that the cluster returns to one Primary and two Replicas.

The mandatory PostgreSQL StatefulSet in namespace `homework`
is not modified by this bonus.
