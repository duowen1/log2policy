import json
import time
import random
from kubernetes import client, config
from concurrent.futures import ProcessPoolExecutor, as_completed

traffics = []


def traffic_from_log(log, source_service_name, source_service_version):
    log = json.loads(log.strip())
    try:
        direction, port, _, destination_service_account = log["upstream_cluster"].split("|")
    except AttributeError:
        return None
    except ValueError:
        return None
    destination_service = destination_service_account.split('.')[0]

    if direction == 'inbound':
        return None

    traffic = dict()
    traffic["source"] = source_service_name
    traffic["version"] = source_service_version
    traffic["path"] = log["path"]
    if traffic["path"] is not None:
        traffic["path"] = traffic["path"].split("?")[0]
    traffic["method"] = log["method"]
    traffic["port"] = port
    traffic["destination"] = destination_service

    if "protocol" in log:
        traffic["protocol"] = log["protocol"]

    return traffic


def logs_to_traffics(logs, pod_name, percent=10):
    pod = pod_name.split("-")

    service_name = '-'.join(pod[0:-3])
    service_version = pod[-3]

    logs = logs.split('\n')

    traffic_counts = 0

    for log in logs:
        n = random.randint(1, percent)
        if n % percent != 0:
            continue
        if log != "" and log[0] == '{':
            traffic_counts += 1
            traffic = traffic_from_log(log, service_name, service_version)
            if traffic is not None:
                traffics.append(traffic)

    return traffic_counts


# Functions:
#   get the log from istio_proxy in the namespace
# Args:
#   namespace: String, the namespace of the application
#   concurrent_flag: Bool, use multi-process to accelerate or not
#   container_name: String, the name of container whose log will be analyzed
#   percent: Int, the rage of sampling = 1/percent
# Returns:
#   traffics: A dictionary List, contains all the traffic in the application
def get_log_from_istio_proxy(namespace="default", concurrent_flag=False, container_name="istio-proxy", percent=1):
    config.load_kube_config()

    v1 = client.CoreV1Api()

    pods = v1.list_namespaced_pod(namespace)

    # start = time.time()

    if not concurrent_flag:
        for pod in pods.items:
            logs = v1.read_namespaced_pod_log(pod.metadata.name, namespace, container=container_name)
            count = logs_to_traffics(logs, pod.metadata.name, percent)
            print(pod.metadata.name, count)

    # Multi-process
    else:
        with ProcessPoolExecutor(max_workers=len(pods.items)) as executor:
            future_count = {
                executor.submit(
                    logs_to_traffics,
                    v1.read_namespaced_pod_log(pod.metadata.name, namespace, container=container_name),
                    pod.metadata.name): pod for pod in pods.items
            }
            for future in as_completed(future_count):
                print(future.result())

    return traffics


def get_log_from_file(namespace="default", concurrent_flag=False, container_name="istio-proxy", percent=10):
    # file_list = ["carts-v1", "carts-db-v1", "catalogue-v1",
    #              "catalogue-db-v1", "front-end-v1", "orders-v1",
    #              "orders-db-v1", "payment-v1", "shipping-v1",
    #              "user-v1", "user-db-v1",
    #              # "catalogue-v2", "shipping-v2", "orders-v2"
    #              ]

    # file_list = ["cart", "product", "stock", "user", "frontend", "order"]

    # file_list = ["details-v1", "productpage-v1", "ratings-v1", "reviews-v1", "reviews-v2", "reviews-v3"]
    # file_list = ["details-v1", "productpage-v1", "ratings-v1", "reviews-v1", "reviews-v2", "reviews-v3", "ratings-v2", "details-v2", "mongodb-v1"]
    # file_list = ["cart-v1", "frontend-v1", "order-v1", "product-v1", "stock-v1", "user-v1"]#, "client-v1", "order-v2", "product-v2"]
    # file_list = ["adservice-v1", "cartservice-v1", "checkoutservice-v1", "currencyservice-v1",
    #              "emailservice-v1", "frontend-v1", "paymentservice-v1", "productcatalogservice-v1",
    #              "recommendationservice-v1", "redis-cart-v1", "shippingservice-v1",
    #              "adservice-v2", "currencyservice-v2", "emailservice-v2"]

    file_list = ["auditlogservice-v1", "customermanagementapi-v1", "invoiceservice-v1", "logserver-v1", "mailserver-v1",
                 "notificationservice-v1", "rabbitmq-v1", "sqlserver-v1", "timeservice-v1", "vehiclemanagementapi-v1", "webapp-v1",
                 "workshopmanagementapi-v1", "workshopmanagementeventhandler-v1"]

    for file in file_list:
        logpath = 'your path'
        with open(logpath+file, "r") as f:
            try:
                logs = f.read()
            except UnicodeDecodeError:
                print(file)
                exit(0)
            count = logs_to_traffics(logs, file + "-xxx-xxxx", percent)
    return traffics
