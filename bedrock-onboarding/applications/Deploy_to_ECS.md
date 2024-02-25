## Deploying Streamlit application to Amazon Elastic Container Service
You can deploy the Streamlit application to Amazon ECS Fargate and below provides steps for the deployment. This requires containerizing the application, creating ECR repository and pushing the created docker image to the repository. You may want to setup Application Load Balancer to front the traffic to ECS service. If you have already created ECR you can directly go to setup steps. If you don't have it created, you can create manually or create one using the given [CloudFormation template](cf_templates/ecs_ecr_alb_creation.yml). Once the stack has been created notedown the ECR repo name by copying from the output and will be used below (ECR_REPOSITORY_NAME).


## Setup Docker environment - SageMaker Studio
You can use a development environment that has docker configured to build the image. Optionally you can use SageMaker Studio's local docker mode for this purpose. However as a pre-requisite docker needs to be enabled for the domian and docker CLI needs to be installed. You can get full instructions in the reference document [here](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-local.html).

Execute below command to enable docker

``aws --region <REGION> sagemaker update-domain --domain-id <DOMAIN_ID>  --domain-settings-for-update '{"DockerSettings": {"EnableDockerAccess": "ENABLED"}}'
``

Copy the docker CLI install script available [here](https://github.com/aws-samples/amazon-sagemaker-local-mode/blob/main/sagemaker_studio_docker_cli_install/sagemaker-distribution-docker-cli-install.sh) to local folder.

Make the install script executable

``
chmod+x sagemaker-distribution-docker-cli-install.sh 
``

Install docker CLI by executing the script

``
./sagemaker-distribution-docker-cli-install.sh 
``

## Setup Docker environment - SageMaker Studio Classic
if you are running this from SageMaker Studio classic, install sm-docker utility to start the build and push the image to ECR

``
pip install sagemaker-studio-image-build 
``

To start the build and push to ECR execute the below command
``
sm-docker build . --repository {ECR_REPOSITORY_NAME}
``

## IAM Permissions:
NOTE:

> For both SageMaker Studio and SageMaker Studio classic, SageMaker domain needs to have permission to push ECR images (Otherwise will retry during docker push for ever) and update ECS service


## Build with Docker

Build your Docker image using the following command. For information on building a Docker file from scratch see the instructions here . You can skip this step if your image is already built. You can check the build image in the list

``
docker build --network sagemaker -t bedrock-app .
docker image ls
``

After the image has been built, check if it can run without any issues by running the following command

``
docker run --network sagemaker bedrock-app
``

You can stop the container by Control + C command.


## Publish to ECR repo

Retrieve an authentication token and authenticate your Docker client to your registry.

``
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com
``

After the build completes, tag your image so you can push the image to this repository:

``
docker tag bedrock-app:latest <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/<ECR_REPOSITORY_NAME>:latest
``

Run the following command to push this image to your newly created AWS repository:
``
docker push <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/<ECR_REPOSITORY_NAME>:latest
``

Update ECS service with cluster and service information as specified in the Cloudformation template. If you have already created, update the names below.

``
aws ecs update-service --cluster bedrock-streamlit-cluster --service bedrock-streamlit --desired-count 2
``

## Clean up (Optional)

To clean-up remove the image pushed to ECR. You can execute the CLI command or remove from AWS Console. You can remove the resources created by deleteting the CloudFormation stack. 

To clean-up the image created locally, execute docker command.

To view the stopped container run the following command
``docker ps -a``

To view the list of images
``docker images``

Remove the container and then the image
```
docker rm <container_id>
docker rmi <image_id>
```
or you can force remove by ``docker rmi -f bedrock-app``


