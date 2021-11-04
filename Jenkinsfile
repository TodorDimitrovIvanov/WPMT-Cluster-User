def app

pipeline{
	agent{
		label 'jenkins-slave-agent-01'
	}
	environment{ 
	dockerRegistry = "docker-registry.wpmt.org"
	dockerUsername = "docker-user"
	}
	// Here we declare that our Jenkins Agent will be 
	// using Python 3.9.2 image from the public Docker registry
	stages{
		// Here we declare the steps of the Pipeline
		stage ('Checkout from GitHub'){
			agent{
				label 'jenkins-slave-agent-01'
			}
			steps{
				checkout scm
			}
		}
		stage('Build Docker image'){
			agent{
				label 'jenkins-slave-agent-01'
			}
			steps{
				script{
					def imageVersion = readFile('VERSION')
					sh """
						docker build -t dev/wpmt-cluster-user:$imageVersion -f Dockerfile .
					"""
				}
			}
		}
		stage('Push Docker image'){
			agent{
				label 'jenkins-slave-agent-01'
			}
			steps{
				script{
					def imageVersion = readFile('VERSION')
					sh """
						dockerPassword=$(env | grep dockerPassword);
						docker login -u $dockerUsername -p $dockerPassword
						docker tag dev/wpmt-cluster-user:$imageVersion $dockerUsername/wpmt-cluster-user:$imageVersion
						docker push $dockerRegistry/$dockerUsername/wpmt-cluster-user:$imageVersion 
					"""
				}
			}
		}
		stage('Provision image'){
			agent{
				label 'jenkins-slave-agent-01'
			}
			steps{
				script{
					// TODO: Add Helm intergration
					echo(message: "Helm integration not yet completed")
				}
			}
		}
	}
}
