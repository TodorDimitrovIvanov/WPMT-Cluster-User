def app

pipeline{
	agent{
		label 'jenkins-slave-agent-01'
	}
	environment{ 
	dockerRegistry = "https://docker-registry.wpmt.org"
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
						docker tag dev/wpmt-cluster-user:$imageVersion $dockerRegistry/$dockerUsername/wpmt-cluster-user:$imageVersion
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
