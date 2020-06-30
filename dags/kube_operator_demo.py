"""An example DAG demonstrating Kubernetes Pod Operator."""

# [START composer_kubernetespodoperator]
import datetime

from airflow import models
from airflow.contrib.kubernetes import secret
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator


# A Secret is an object that contains a small amount of sensitive data such as
# a password, a token, or a key. Such information might otherwise be put in a
# Pod specification or in an image; putting it in a Secret object allows for
# more control over how it is used, and reduces the risk of accidental
# exposure.

# [START composer_kubernetespodoperator_secretobject]
secret_env = secret.Secret(
    # Expose the secret as environment variable.
    deploy_type='env',
    # The name of the environment variable, since deploy_type is `env` rather
    # than `volume`.
    deploy_target='SQL_CONN',
    # Name of the Kubernetes Secret
    secret='airflow-secrets',
    # Key of a secret stored in this Secret object
    key='sql_alchemy_conn')
secret_volume = secret.Secret(
    'volume',
    # Path where we mount the secret as volume
    '/var/secrets/google',
    # Name of Kubernetes Secret
    'service-account',
    # Key in the form of service account file name
    'service-account.json')
# [END composer_kubernetespodoperator_secretobject]

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)

# If a Pod fails to launch, or has an error occur in the container, Airflow
# will show the task as failed, as well as contain all of the task logs
# required to debug.
with models.DAG(
        dag_id='composer_sample_kubernetes_pod',
        schedule_interval=datetime.timedelta(days=1),
        start_date=YESTERDAY) as dag:

    pi = KubernetesPodOperator(
            dag=dag,
            task_id='pi',
            name='pi',
            namespace='default',
            image='perl',
            cmds=['perl'],
            arguments=['-Mbignum=bpi', '-wle', 'print bpi(2000)'],
            secrets=[],
            # Labels to apply to the Pod.
            labels={'app': 'airflow-example'},
            # Timeout to start up the Pod, default is 120.
            startup_timeout_seconds=120,
            # If true, logs stdout output of container. Defaults to True.
            get_logs=True
        )

    passing = KubernetesPodOperator(
                dag=dag,
                name="passing",
                task_id="passing-task",
                namespace='default',
                image="python:3.6",
                cmds=["python","-c"],
                arguments=["print('hello world')"],
                get_logs=True,
                labels={'app': 'airflow-example'}
            )

    failing = KubernetesPodOperator(
                dag=dag,
                name="fail",
                task_id="failing-task",
                namespace='default',
                image="ubuntu:latest",
                cmds=["python","-c"],
                arguments=["print('hello world')"],
                labels={'app': 'airflow-example'},
                get_logs=True,
                image_pull_policy='Always',
            )

    pi >> passing
    pi >> failing