
pipeline{
	def app
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
				app = docker.build("dev/docker-user:${imageVERSION}")
			}
		}
		stage('Push Docker image'){
			withDockerRegistry("${dockerRegistry}", "docker-registry"){
				app.push("${dockerRegistry}/${dockerUsername}/${imageVersion}")
			}
		}
	}
}
