#!/usr/bin/env bash
 


docker-compose stop 
docker-compose rm 

VOLUME_NAMES=$(docker volume ls --format='{{.Name}}' | egrep -v 'thesis') 

echo "WARNING: THE FOLLOWING DOCKER VOLUMES WILL BE CLEANED" 
echo "$VOLUME_NAMES"

select yn in "Yes" "No"; do
    case $yn in
        Yes ) docker volume rm $VOLUME_NAMES; break;;  
        No ) exit;;
    esac
done

