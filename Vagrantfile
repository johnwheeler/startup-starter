# -*- mode: ruby -*-
# vi: set ft=ruby ts=2 sw=2 expandtab :

# Project name
PROJECT = ENV.fetch("PROJECT", "flask-live-starter")

# Project directory
PROJECT_DIR="/home/vagrant/workspace/#{PROJECT}"

# Build directory
BUILD_SCRIPTS="#{PROJECT_DIR}/build_scripts"

# UID
UID = Process.euid

# Port to access the app outside of the development container
VAGRANT_PORT=ENV.fetch('VAGRANT_PORT', '8000')

# Vagrant config for running the boxes
ENV['VAGRANT_NO_PARALLEL'] = 'yes'
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'

# Environment variable
DOCKER_ENV = {

  # Application
  'APP_PATH'     => PROJECT_DIR,
  'APP_NAME'     => PROJECT,
  'APP_USER'     => "vagrant",
  'HOST_USER_UID'=> UID,
  'PROJECT_DIR'  => PROJECT_DIR,
  'SECRET_KEY'   => 'MyBelovedPrecious',

  # Database
  'DB_ENGINE'    => "postgres",
  'DB_HOST'      => "db",
  'DB_NAME'      => "vagrant",
  'DB_USERNAME'  => "vagrant",
  'DB_PASSWORD'  => "vagrant",

  # SMPT
  'MAIL_SERVER' => "smtp.sendgrid.net",
  'MAIL_USERNAME' => "vagrant",
  'MAIL_PASSWORD' => "vagrant",
  'ADMIN_EMAIL' => "vagrant@vagrant.com",

  # Debug
  'DEV_MODE'     => "true",
  'FLASK_CONFIG' => "development",

  # Virtualenv
  'VIRTUAL_ENV_PATH' => "#{PROJECT_DIR}/venv",
  'ENV_NAME'         => "devdocker",
}

Vagrant.configure(2) do |config|

  config.ssh.forward_agent = true
  config.ssh.host = "127.0.0.1"
  config.ssh.port = 2200

  # Postgres container
  config.vm.define "db" do |db|
    db.vm.provider "docker" do |d|
      # For MacOS users. Prevent vagrant from using a VB-based box
      d.force_host_vm = false

      d.image = "postgres:9.5"
      d.name = "#{PROJECT}_db"
      d.ports = ["5432:5432"]
      d.env = {
        "POSTGRES_PASSWORD" => DOCKER_ENV['DB_PASSWORD'],
        "POSTGRES_USER" => DOCKER_ENV['DB_USERNAME'],
        "POSTGRES_DB" => DOCKER_ENV['DB_NAME'],
      }
    end
  end


  # Development container
  config.vm.define "dev", primary: true do |app|

    app.vm.provider "docker" do |d|
      # For MacOS users. Prevent vagrant from using a VB-based box
      d.force_host_vm = false

      # Flask app listens on 8000, redirect on VAGRANT_PORT on host
      d.ports = ["#{VAGRANT_PORT}:8000"]
      d.image = "allansimon/allan-docker-dev-python"
      d.name = "#{PROJECT}_dev"

      # Link to database container
      d.link "#{PROJECT}_db:#{DOCKER_ENV['DB_HOST']}"
      d.volumes =  [
        "#{ENV['PWD']}/:#{PROJECT_DIR}"
      ]
      d.env = DOCKER_ENV
      d.has_ssh = true
    end

    # so that we can git clone from within the docker
    app.vm.provision "file", source: "~/.ssh/id_rsa", destination: ".ssh/id_rsa"

    # so that we can git push from inside the docker
    app.vm.provision "file", source: "~/.gitconfig", destination: ".gitconfig"

    # we can't copy in /root using file provisionner
    # hence the usage of shell
    app.vm.provision "permits-root-to-clone", type: "shell" do |s|
      s.inline = "cp /home/vagrant/.ssh/id_rsa ~/.ssh/id_rsa"
    end

    # Dev environment provisioning
    app.vm.provision :shell, :inline => <<-END
      set -eu
      sudo cat /etc/container_environment.sh | grep -v 'export _=' | source /dev/stdin
      apt-get update -y

      # Configure the container behavior at startup/boot

      ZSHRC=/home/vagrant/.zshrc
      echo "# Go directly to the project directory"  >> $ZSHRC
      echo 'cd #{PROJECT_DIR}' >>  $ZSHRC
      echo "# Activate the virtualenv" >> $ZSHRC
      echo "source #{DOCKER_ENV['VIRTUAL_ENV_PATH']}/bin/activate" >>  $ZSHRC

      # cd to the project directory
      cd #{PROJECT_DIR}

      # Install debian dependencies
      sudo apt install -y libpq-dev python-dev libffi-dev libssl-dev

      # Upgrade pip
      pip install -U pip

      # Install virtualenv
      pip install virtualenv

      # Create virtualenv
      virtualenv #{DOCKER_ENV['VIRTUAL_ENV_PATH']}

      # Activate virtualenv (see https://github.com/pypa/virtualenv/issues/150)
      set +o nounset
      source #{DOCKER_ENV['VIRTUAL_ENV_PATH']}/bin/activate
      set -o nounset

      # Install app requirements
      pip install -r requirements.txt

      # chown the vagrant home to vagrant user. This prevents permission issues
      chown -R vagrant:vagrant /home/vagrant

      echo "Run 'vagrant ssh' to access the development container."
    END

    # SSH config. No password required.
    app.ssh.username = "vagrant"
    app.ssh.password = ""
  end
end
