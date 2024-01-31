# PREREQUISITES
Python3\
Docker\
Kubectl\
AWS CLI\
Programmatic Access (ACCESS_KEY_ID, SECRET_ACCESS_KEY)\
PIP(Preferred Installer Program)

All the steps are given based on the windows OS

## Step 1:
```
git clone https://github.com/Danishbansal-cmd/Cloud_Native_Application
```

Clone an application of Python to demonstrate the CPU Utilization and Memory Utilization

The application uses different Libraries like
psutil - https://pypi.org/project/psutil/\
It a cross-platform library to retrieve the running processes and system utilizations

flask - https://pypi.org/project/Flask/\
It is lightweight WSGI(Web Server Gateway Interface) for the Web application framework

boto3 - https://pypi.org/project/boto3/\
It is AWS SDK for the Python which allows the developers and the practitioners to create the application based on python with the use of Amazon Web Services and Resources like ECS, EKS, Amazon S3, Amazon Elastic Cloud Compute, and many more.

plotly - https://pypi.org/project/plotly/\
plotly.py is an interactive browser-based library built on top of plotly.js, it has used more than 30 chart type, incuding scientific charts, 3d charts and more

## Step 2:
Copy the code into the file and name it "app.py"

```
import psutil
from flask import Flask, render_template

app = Flask(__name__)
app.debug = True

@app.route("/")
def index():
    cpu_percent = psutil.cpu_percent(interval=2)
    mem_precent = psutil.virtual_memory().percent
    Message = None
    if cpu_percent > 80 or mem_precent > 80:
        Message = "High CPU or Memory Utilization detected. Please Scale up"
    return render_template("index.html", cpu_metric=cpu_percent,mem_metric=mem_precent,message=Message)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
```
Run the command Specified below, it is used to install all the dependencies that are listed there
```
pip install -r requirements.txt
```
It is used to enable the debugger, so that if the server find any changes, will show an interactive debugger during the error or a request
```
app.debug = True
```
After it is successful, it will run on the [localhost:5000](http://localhost:5000/), visit this link to view your application

## Step 3:
Now we will create the docker file which will be used to create the image of the docker\
Docker image is used to run the container\
Copy the code into the file and name it "Dockerfile"

```
FROM python:3.8-slim

WORKDIR /app

COPY  requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
```

First line "FROM python:3.8-slim" which is used to get the base image Python from the docker [registry](https://hub.docker.com/_/python), there are many images that one can use but prefer to use the one which has low image size

Last line CMD '--host=0.0.0.0' is used to make the docker the port forwarding to the specified port, otherwise the flask application will only be accessible from within the container not the outside\
localhost has the ip'127.0.0.1'

To create the docker image run the command
```
docker build -t <any_custom_image_name_you_want_to_specify>
```

## Step 4:
Run the command specified below, to check all the docker images
```
docker images
```
To run the container of the image that we have just created, run the command specified below
```
docker run -p 5000:5000 <docker_image_id>
```
It will the start Flask application on the [localhost:5000](http://localhost:5000/). Navigate to the link on your browser to view your application running

## Step 5:
Copy the code to new file and name it 'ecr.py'\
It is the code to create a new repository in the AWS ECR
```
import boto3

client = boto3.client('ecr')

repository_name = "my_cloud_native_repo"
response = client.create_repository(repositoryName=repository_name)

repository_uri = response["repository"]['repositoryUri']
print(repository_uri)
```
Run the python file with "python ecr.py" command
Learn more about the boto3 library go the documentation of [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
If it runs successfully it will return the result with uri of the repository or registry created.

## Step 6:
Push the docker image to the AWS ECR repository
```
docker push <ecr_repo_uri>:<tag>
```

To proper set of commands to push the registry from the local to the ECR\
![ViewCommands](https://drive.google.com/file/d/11tOfn96wdMK0r2oOgqw6kP5mHP2ee20y/view?usp=sharing)

## Step 7:
Copy the code specified below and name it "eks.py"
```
#create deployment and service
from kubernetes import client, config

# Load Kubernetes configuration
config.load_kube_config()

# Create a Kubernetes API client
api_client = client.ApiClient()

# Define the deployment
deployment = client.V1Deployment(
    metadata=client.V1ObjectMeta(name="my-flask-app"),
    spec=client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(
            match_labels={"app": "my-flask-app"}
        ),
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"app": "my-flask-app"}
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="my-flask-container",
                        image="your_image",
                        ports=[client.V1ContainerPort(container_port=5000)]
                    )
                ]
            )
        )
    )
)

# Create the deployment
api_instance = client.AppsV1Api(api_client)
api_instance.create_namespaced_deployment(
    namespace="default",
    body=deployment
)

# Define the service
service = client.V1Service(
    metadata=client.V1ObjectMeta(name="my-flask-service"),
    spec=client.V1ServiceSpec(
        selector={"app": "my-flask-app"},
        ports=[client.V1ServicePort(port=5000)]
    )
)

# Create the service
api_instance = client.CoreV1Api(api_client)
api_instance.create_namespaced_service(
    namespace="default",
    body=service
)
```

Make sure to change the "your_image" to your uri, that you can get on this page\
![page](https://drive.google.com/file/d/11tOfn96wdMK0r2oOgqw6kP5mHP2ee20y/view?usp=sharing)


## Step 8:
Create the AWS EKS cluster\
Type the name of the cluster and choose the role if it has created\
Otherwise create the IAM role with "AWS Service" and select the use case to "EKS Cluster" and create it\
After choosing the IAM role make a selection in the EKS Cluster with the appropriate roles assigned to it\
![createEksCluster](https://drive.google.com/file/d/1sLNDn9yMQM_cbC1AVBFESdWgVat9dcN3/view?usp=sharing)\
Then choose next

On the next page choose the Default VPC and default Security Group with Ingress rule of "5000" port
And choose next util you see "create" Button

## Step 9:
Now open the EKS Cluster that we have created and choose the "Compute" Tab\
Click on "Add node group" Button to create the node\
![createNodeGroup](https://drive.google.com/file/d/1jkMF_toS95I-NUX8guw0JlWOo7zaUI-z/view?usp=sharing)\
Select the appropriate role if it has been created\
Otherwise create the role with "AWS Service" as selected, select the use case to "EC2" and attach the "AmazonEKSWorkerNodePolicy", "AmazonEC2ContainerRegistryReadOnly" policies to the role\
Choose next Button and dont change the other configurations, leave it as they are,\
Don't change the Instance type from t3.medium to t2.micro or less\
Otherwise the node group will not get created\
Choose the next button until you see the create button\

Run the file using the "python eks.py" command

Check by running some of the following commands
```
kubectl get deployment -n default (check deployments)
kubectl get service -n default (check service)
kubectl get pods -n default (to check the pods)
```

To forward your pod to the local run the command
```
kubectl port-forward service/<service_name> 5000:5000
```

