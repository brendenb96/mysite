
web:
	apt-get update
	apt-get -y install python-pip python-dev build-essential
	apt-get -y install sshpass
	apt-get install phpmyadmin -y
	apt-get install apache2 -y
	apt-get install mysql-server mysql-client -y
	apt-get install php5 libapache2-mod-php5 php5-mysql -y
	service apache2 restart
	pip install --upgrade pip 
	pip install --upgrade virtualenv
	pip install Django==1.11