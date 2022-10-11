# noahs-doves
This is a pipeline. Scrape data from Internet and then pubulish message to middleware(DAPR). Run the programes on K8S.
![image](https://user-images.githubusercontent.com/75282285/150705453-9d2bb368-0747-4761-ace3-a91961d8728f.png)

# Set the valuable of Env on K8S
Set the valuable of env with configmap.yaml and yaml.yaml.

These two files have sent by Slack.
![image](https://user-images.githubusercontent.com/75282285/150704268-caab8678-ec21-41e7-ac92-ef77a663d852.png)

# Intatll the Rids database for Dapr
~~~
$ helm repo add bitnami https://charts.bitnami.com/bitnami
$ helm repo update
$ helm install redis bitnami/redis
~~~
![image](https://user-images.githubusercontent.com/75282285/150704314-d7ec9132-a96b-49e3-a506-a19d92541659.png)

~~~
kubectl get pods
~~~
![image](https://user-images.githubusercontent.com/75282285/150704338-f0a0f5f1-a06e-4aac-ad52-32956c97d819.png)


# How to run it on K8S + Dapr
Build the container with noahs-doves-dapr.yaml
~~~
kubectl apply -f  noahs-doves-dapr.yaml
~~~
![image](https://user-images.githubusercontent.com/75282285/150703819-724024ce-052f-4eb2-9d44-9160d2bff9fd.png)

# Run on Dapr
![image](https://user-images.githubusercontent.com/75282285/150703831-c4deaed3-daf3-4db8-88d3-be36aafa13d3.png)

# Visit Scrapyd
~~~
kubectl port-forward  noahs-doves-85764bd66-mhljb    8090:3500
~~~
then visit http://127.0.0.1:8090/v1.0/invoke/noahs-doves/method/
![image](https://user-images.githubusercontent.com/75282285/150703868-c055b7a3-f89b-44cc-a4d9-bdc0ef8e51cc.png)


# Send an order to it to scrape
~~~
kubectl port-forward noahs-doves-f45bb7fc8-4ghcf  8090:3500
~~~
![image](https://user-images.githubusercontent.com/75282285/150703926-0bad937b-f009-46c2-b139-6de6ee01920a.png)

Then send the order to scrape the christiancharityjobs website.
~~~
curl http://127.0.0.1:8090/v1.0/invoke/noahs-doves/method/schedule.json -d project=jobpostings -d spider=christiancharityjobs
~~~

Also can send the order to scrape the christiancareerscanada website
~~~
curl http://127.0.0.1:8090/v1.0/invoke/noahs-doves/method/schedule.json -d project=jobpostings -d spider=christiancareerscanada
~~~

# Check the log of Noahs
~~~
kubectl logs noahs-doves-f45bb7fc8-4ghcf  -c noahs-doves
~~~
Also can see the detail log on browser.
![image](https://user-images.githubusercontent.com/75282285/150704041-11c32dfe-593e-476f-b2df-f44f919c8cff.png)


