sudo yum -y update
sudo yum -y install epel-release
sudo yum -y groupinstall ‘Development Tools’ 
sudo yum -y install cyrus-sasl-ldap cyrus-sasl-devel openldap-devel \
	libxslt libxslt-devel libxslt-python git gcc graphviz-devel \
	python-virtualenv python-virtualenvwrapper php-devel php-pear \
	python-devel python-pip openssl-devel \
	ImageMagick ImageMagick-devel libevent-devel compat-libevent14-devel