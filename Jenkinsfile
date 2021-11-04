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
					app = docker.build("dev/wpmt-cluster-user:$imageVersion")
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
					app.tagg("dev/wpmt-cluster-user:$imageVersion", "$dockerRegistry/$dockerUsername/$imageVersion")
					app.push("$dockerRegistry/$dockerUsername/$imageVersion")
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
