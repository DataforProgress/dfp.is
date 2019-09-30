sudo apt-get update

# ElasticSearch
sudo apt install openjdk-8-jdk
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo sh -c 'echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" > /etc/apt/sources.list.d/elastic-7.x.list'
sudo apt update
sudo apt install elasticsearch

sudo /bin/systemctl enable elasticsearch.service
sudo systemctl start elasticsearch.service


# Flask stack

sudo apt-get install python3-pip python3-dev nginx
sudo pip3 install virtualenv

virtualenv data-infra

source data-infra/bin/activate

pip install -r requirements.txt
python load_es.py

# assumes data-infra.service with correct user for system is deployed

cp data-infra.service /etc/systemd/system/
sudo systemctl enable data-infra
sudo systemctl start data-infra


