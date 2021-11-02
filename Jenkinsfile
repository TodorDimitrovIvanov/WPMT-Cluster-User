 def app

pipeline{

	environment{ 
	dockerRegistry = "https://docker-registry.wpmt.org"
	dockerUsername = "docker-user"
	}
	agent{
	label 'jenkins-slave-agent-01'
	}
	// Here we declare that our Jenkins Agent will be 
	// using Python 3.9.2 image from the public Docker registry
	stages{
		// Here we declare the steps of the Pipeline
		stage ('Checkout from GitHub'){
			steps{
				checkout scm
				script{
					def imageVersion = readFile('VERSION')
				}
			}
		}
		stage('Build Docker image'){
			steps{
				script{
					sh """
						docker build -t dev/wpmt-cluster-user:$imageVersion -f Dockerfile .
					"""
				}
			}
		}
		stage('Push Docker image'){
			steps{
				script{
					sh """
						docker tag dev/wpmt-cluster-user:$imageVersion $dockerRegistry/$dockerUsername/$imageVersion
						docker push $dockerRegistry/$dockerUsername/$imageVersion 
					"""
				}
			}
		}
		stage('Provision image'){
			steps{
				script{
					// TODO: Add Helm intergration
					echo(message: "Helm integration not yet completed")
				}
			}
		}
	}
}
