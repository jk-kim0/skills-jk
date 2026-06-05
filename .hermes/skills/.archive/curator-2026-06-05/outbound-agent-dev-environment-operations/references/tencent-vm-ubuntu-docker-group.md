# Tencent VM ubuntu Docker group baseline

Context: Outbound Agent Tencent dev VMs (`dev-seoul`, `dev-tokyo`) run Docker Engine with `/var/run/docker.sock` owned by `root:docker` mode `660`. GitHub Actions SSH workflows connect as the default `ubuntu` account.

Durable lesson:

- The VM baseline should make `ubuntu` a member of the `docker` group so read-only diagnostics and DB checks can run `docker ps`, `docker exec`, and `docker compose` without `sudo`.
- This avoids per-workflow `sudo docker` patches when the real problem is host account membership.
- Root-only operations still need `sudo`: reading/editing `/etc/outbound-agent/*.env`, systemd/nginx/certbot operations, and host package/service changes.
- Group membership applies to new login/session contexts. Existing SSH sessions may not see the new group list.

Apply/verify on a VM:

```bash
sudo groupadd -f docker
sudo usermod -aG docker ubuntu
getent group docker
runuser -u ubuntu -- docker ps --format '{{.Names}}'
stat -c '%U:%G %a %n' /var/run/docker.sock
```

Expected evidence shape:

```text
after_group=docker:x:<gid>:ubuntu
docker_socket=root:docker 660 /var/run/docker.sock
ubuntu_docker_ps=outbound-front, outbound-agent-postgres
```

When direct SSH from the agent runtime is blocked by Security Group ingress but Tencent Cloud TAT agent is online, use TAT `RunCommand` as an operational path for this host-level fix, then query `DescribeInvocationTasks --HideOutput False` for evidence. Do not record secrets in repo docs or PR bodies.
