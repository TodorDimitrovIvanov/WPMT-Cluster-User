echo "Build version: "
read buildVersion
repoName="wpmt-cluster-user"
buildCommand="docker build -t dev/$repoName:$buildVersion -f Dockerfile ."
tagCommand="docker tag dev/$repoName:$buildVersion docker-registry.wpmt.org/docker-user/$repoName:$buildVersion"
pushCommand="docker push docker-registry.wpmt.org/docker-user/$repoName:$buildVersion"
$buildCommand
$tagCommand
$pushCommand
