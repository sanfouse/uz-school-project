import json
import logging
import os
import uuid

from kubernetes import client, config
from kubernetes.client import V1Job, ApiException, V1DeleteOptions, V1Volume, V1VolumeMount, V1ConfigMapVolumeSource

log = logging.getLogger(__name__)


class K8sSettings:
    namespace: str = os.getenv("NAMESPACE", "default")
    labels: dict[str, str] = {"scraper": "true"}
    timeout: int = 60


settings = K8sSettings()


def _load_k8s_config() -> None:
    try:
        config.load_incluster_config()
        log.info("Loaded in-cluster Kubernetes configuration.")
    except config.ConfigException:
        config.load_kube_config()
        log.info("Loaded local kubeconfig.")


_load_k8s_config()

core_client = client.CoreV1Api()
batch_client = client.BatchV1Api()


def create_job(
    job_name: str,
    container_name: str,
    image: str,
    env_vars: list[dict[str, str]],
    cpu_limit: str = "1",
    mem_limit: str = "1024Mi",
    words: list[str] | None = None,  # новый параметр
) -> V1Job:
    log.info(f"Creating job '{job_name}' using image '{image}'...")

    volumes = []
    volume_mounts = []

    if words:
        config_map_name = f"{job_name}-words-{uuid.uuid4().hex[:6]}"

        core_client.create_namespaced_config_map(
            namespace=settings.namespace,
            body=client.V1ConfigMap(
                metadata=client.V1ObjectMeta(name=config_map_name),
                data={"words.json": json.dumps(words, ensure_ascii=False)},
            ),
        )

        volumes.append(
            V1Volume(
                name="words-volume",
                config_map=V1ConfigMapVolumeSource(name=config_map_name),
            )
        )
        volume_mounts.append(
            V1VolumeMount(
                name="words-volume",
                mount_path="/app/config",
                read_only=True,
            )
        )

    return batch_client.create_namespaced_job(
        namespace=settings.namespace,
        body=client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name, labels=settings.labels),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels=settings.labels),
                    spec=_pod_spec(
                        container_name,
                        image,
                        env_vars,
                        cpu_limit,
                        mem_limit,
                        volumes=volumes,
                        volume_mounts=volume_mounts,
                    ),
                ),
                backoff_limit=3,
                ttl_seconds_after_finished=86400,
            ),
        ),
        _request_timeout=settings.timeout,
    )


def list_jobs(prefix: str | None = None, status: str | None = None) -> list[V1Job]:
    jobs = batch_client.list_namespaced_job(
        namespace=settings.namespace, label_selector="scraper=true"
    ).items

    if prefix:
        jobs = [j for j in jobs if j.metadata.name.startswith(prefix)]

    if status:
        status = status.lower()
        jobs = _filter_jobs_by_status(jobs, status)

    return jobs


def _filter_jobs_by_status(jobs: list[V1Job], status: str) -> list[V1Job]:
    if status == "pending":
        return [
            j
            for j in jobs
            if j.status.active and not (j.status.succeeded or j.status.failed)
        ]
    if status == "running":
        return [j for j in jobs if j.status.active]
    if status == "finished":
        return [j for j in jobs if j.status.succeeded or j.status.failed]
    return jobs


def delete_job(name: str, grace_period_seconds: int = 60) -> None:
    try:
        batch_client.delete_namespaced_job(
            name=name,
            namespace=settings.namespace,
            body=V1DeleteOptions(
                propagation_policy="Foreground",
                grace_period_seconds=grace_period_seconds,
            ),
        )
        log.info(f"Deleted job '{name}'.")
    except ApiException as e:
        log.error(f"Failed to delete job '{name}': {e}")
        raise


def get_job_pod_name(job_name: str) -> str | None:
    pods = core_client.list_namespaced_pod(
        namespace=settings.namespace, label_selector=f"job-name={job_name}"
    ).items
    return pods[0].metadata.name if pods else None


def get_job_logs(job_name: str) -> str:
    pod_name = get_job_pod_name(job_name)
    if not pod_name:
        return f"No pods found for job '{job_name}'"

    try:
        return core_client.read_namespaced_pod_log(
            name=pod_name, namespace=settings.namespace
        )
    except ApiException as e:
        log.warning(f"Failed to get logs for job '{job_name}': {e}")
        return f"Error getting logs: {e}"


def _pod_spec(
    container_name: str,
    image: str,
    env_vars: list[dict[str, str]],
    cpu_limit: str,
    mem_limit: str,
    volumes: list[V1Volume] | None = None,
    volume_mounts: list[V1VolumeMount] | None = None,
) -> client.V1PodSpec:
    return client.V1PodSpec(
        security_context=client.V1PodSecurityContext(
            run_as_non_root=True,
            run_as_user=101,
        ),
        containers=[
            client.V1Container(
                name=container_name,
                image=image,
                image_pull_policy="IfNotPresent",
                env=env_vars,
                security_context=client.V1SecurityContext(
                    allow_privilege_escalation=False,
                    capabilities=client.V1Capabilities(drop=["ALL"]),
                    run_as_non_root=True,
                    run_as_user=101,
                ),
                resources=client.V1ResourceRequirements(
                    requests={"cpu": "0.5", "memory": "512Mi"},
                    limits={"cpu": cpu_limit, "memory": mem_limit},
                ),
                volume_mounts=volume_mounts or [],
            )
        ],
        volumes=volumes or [],
        restart_policy="Never",
    )
