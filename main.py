from typing import Optional
import json
import requests
import mysql.connector
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_backend
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import uvicorn


app = FastAPI()

__master_url__ = "https://master.wpmt.org"

__cluster_name__ = "cluster-eu01.wpmt.org"
__cluster_url__ = "https://cluster-eu01.wpmt.org"
__cluster_logger_url__ = "http://cluster-eu01.wpmt.tech/log/save"
__cluster_locale__ = "EU"
__cluster_user_count__ = None

__mysql_host__ = "localhost"
__mysql_db__ = "cluster_eu01"
__mysql_user__ = "cluser_eu01_user"
# The API should receive the password via system's environment variable
# This variable is set by Kubernetes via the "secretGenerator.yaml" file
# Source: https://stackoverflow.com/questions/60343474/how-to-get-secret-environment-variables-implemented-by-kubernetes-into-python
# Temporarily disabled:
#   __mysql_pass__ = environ['MYSQL_USER_PASSWORD']
__mysql_pass__ = "kP6hE3zE7aJ7nQ6i"

__app_headers__ = {
    'Host': 'cluster-eu01.wpmt.org',
    'User-Agent': 'WPMT-Auth/1.0',
    'Referer': 'http://cluster-eu01.wpmt.org/user',
    'Content-Type': 'application/json'
}


def send_to_logger(err_type, message, client_id: "None", client_email: "None"):
    # TODO: Find a way to get the user's IP address and add it to the message
    print("Message: ", message, "Type: ", err_type)
    global __app_headers__
    body = {
        "client_id": client_id,
        "email": client_email,
        "type": "access",
        "message": message
    }
    send_request = requests.post(__cluster_logger_url__, data=json.dumps(body), headers=__app_headers__)

#################
    # Router
#################

# Here we define the format of the POST requests that we expect to receive in order to interact with the API service
class UserSignup(BaseModel):
    name: str
    email: str
    password: str
    service: str
    country: str
    locale: str
    notifications: int
    promos: int


class UserRetrieve(BaseModel):
    email: str
    client_id: Optional[str]


@app.post("/user/add", status_code=200)
async def signup(user: UserSignup):
    post_data_dict = user.dict()
    # Here the cluster_uid_generate function will generate a new key pair
    # Save the key pair within the DB along with the other Client details
    # And if successful returns True
    if cluster_uid_generate(post_data_dict['name'], post_data_dict['email'], post_data_dict['password'],
                    post_data_dict['service'], post_data_dict['country'], post_data_dict['locale'],
                    post_data_dict['notifications'], post_data_dict['promos']):
        # If the function was completed properly and returned True
        # Then we should return a 200 OK code to the WPMT User API
        return {
            "Response": "User registration completed!"
        }
    else:
        message = "[Cluster][Error][Signup][01]: Error during the signup process. Missing parameters!"
        send_to_logger("error", message, client_id="None", client_email="None")
        raise HTTPException(status_code=502, detail="Error during signup")



@app.post("/user/get", status_code=200)
async def user_retrieve(retrieve: UserRetrieve):
    post_data_dict = retrieve.dict()

    if post_data_dict['email'] is not None or "":
        result = mysql_user_get(post_data_dict['email'])
        return {
            "Results": result
        }
    elif post_data_dict['client_id'] is not None or "":
        result = mysql_user_get(post_data_dict['client_id'])
        return {
            "Results": result
        }
    else:
        return{
            "Error": "Missing 'email' or 'ID' identifier!"
        }


def mysql_details_get():
    # TODO: Here we should retrieve the global MySQL details that are set in Kubernetes
    # TODO: And apply them to the global variables above
    pass


def mysql_user_add(client_id: str,  email: str, pub_key: str, priv_key: str):
    # Source: https://pynative.com/python-mysql-database-connection/
    if None not in [client_id, email, pub_key, priv_key]:
        try:
            connection = mysql.connector.connect(
                host=__mysql_host__,
                database=__mysql_db__,
                user=__mysql_user__,
                password=__mysql_pass__)
            if connection.is_connected():
                # Here we have to execute the Query for adding new users to the DB
                cursor = connection.cursor()
                mysql_insert_query = "INSERT INTO users (client_id, client_email, client_pub_key, client_priv_key) VALUES (%s, %s, %s, %s)"
                mysql_data = (client_id, email, pub_key, priv_key)
                cursor.execute(mysql_insert_query, mysql_data)
                connection.commit()
                message = "[Cluster][DB][Info]: Added user [" + email + "]."
                send_to_logger("info", message, client_id, email)
        except mysql.connector.Error as e:
            message = "[Cluster][Error][DB][01][mysql_user_add][" + email + "]: Error while starting the K8S MySQL Connection! Full error: [" + str(e) + "]."
            send_to_logger("error", message, client_id, email)
        finally:
            if connection.is_connected():
                connection.close()
    else:
        message = "[Cluster][Error][Signup][01][mysql_user_add]: Error during the signup process. Missing parameters!"
        send_to_logger("error", message, client_id=None, client_email=None)


def mysql_user_get(identifier: str):
    if identifier is not None or "":
        try:
            connection = mysql.connector.connect(
                host = __mysql_host__,
                database = __mysql_db__,
                user = __mysql_user__,
                password = __mysql_pass__)
            if connection.is_connected():
                cursor = connection.cursor()
                mysql_search_query = "SELECT * FROM users WHERE client_email = %s"
                data = identifier
                cursor.execute(mysql_search_query, (data,))
                result = cursor.fetchall()
                return result
        except mysql.connector.Error as e:
            message = "[Cluster][Error][DB][01][mysql_user_get][" + identifier + "]: Error while starting the K8S MySQL Connection! Full error: [" + str(e) + "]."
            send_to_logger("error", message, client_id=identifier, client_email=identifier)


def mysql_user_settings_set(client_id: str, mail_notifications: int, service_type: str, locale: str, promos: int):
    if None not in [client_id, mail_notifications, service_type, locale, promos]:
        try:
            connection = mysql.connector.connect(
                host=__mysql_host__,
                database=__mysql_db__,
                user=__mysql_user__,
                password=__mysql_pass__
            )
            if connection.is_connected():
                # Here we have to execute the Query for adding new users to the DB
                cursor = connection.cursor()
                mysql_insert_query = "INSERT INTO user_settings (client_id, mail_notifications, service_type, locale, promos) VALUES (%s, %s, %s, %s, %s)"
                mysql_data = (client_id, mail_notifications, service_type, locale, promos)
                cursor.execute(mysql_insert_query, mysql_data)
                connection.commit()
                message = "[Cluster][DB][Info]: Added user [" + client_id + "]."
                send_to_logger("info", message, client_id, email="None")
        except mysql.connector.Error as e:
            message = "[Cluster][Error][DB][01][mysql_user_settings_set][" + client_id + "]: Error while starting the K8S MySQL Connection! Full error: [" + str(e) + "]."
            send_to_logger("error", message, client_id=client_id, client_email="None")
        finally:
            if connection.is_connected():
                connection.close()
    else:
        message = "[Cluster][Error][Signup][01][mysql_user_settings_set]: Error during the signup process. Missing parameters!"
        send_to_logger("error", message, client_id=None, client_email=None)
    # TODO: Pass the results to the WPMT User API for further processing


def cluster_keys_generate():
    # Source: https://stackoverflow.com/a/39126754
    key = rsa.generate_private_key(
        backend=crypto_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption()
    )
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return [public_key, private_key]


def cluster_uid_generate(name: str, email: str, password: str, service: str, country: str, locale: str, notifications: int, promos: int):
    # Here the notifications and promos params should be either a 0 or 1.

    if None not in [name, email, password, service, country, locale, notifications, promos]:
        # Get last user ID
        if cluster_get_user_count():
            # DEBUG: Potential issue here with adding an Int to the received result (could be string)
            global __cluster_user_count__
            new_user_num = __cluster_user_count__[0][0] + 1
            generated_uid = __cluster_locale__ + "-UID-" + str(new_user_num).zfill(9)
            # This is a list of the public (1st) and private(2nd) keys:
            generated_keys = cluster_keys_generate()

            # Here we add the new user to the DB along with the keys:
            mysql_user_add(generated_uid, email, generated_keys[0], generated_keys[1])
            # And then we save the user defined settings
            mysql_user_settings_set(generated_uid, notifications, service, locale, promos)

            # Send the registered users and details to the Master DB
            # Source: https://stackoverflow.com/questions/10768522/python-send-post-with-header
            url = __master_url__ + "/api/user/signup"
            headers = {
                'Host': 'master.wpmt.tech',
                'User-Agent': 'WPMT-Cluster/1.0',
                'Referer': 'https://cluster-eu01.wpmt.tech/api/user/signup',
                'Content-Type': 'application/json'
            }
            body = {
                'client_id': generated_uid,
                'name': name,
                'email': email,
                'service': service,
                'password': password,
                'country': country,
                'locale': locale,
                'notifications': notifications,
                'promos': promos,
            }
            # TODO: Temporarily disabled until we get the master server running
            # sent_request = requests.post(url, data=json.dumps(body), headers=headers)

            # End of sending to the Master DB
            return True
        else:
            return "[Cluster][API][Err][02]: Couldn't retrieve user count."
    else:
        message = "[Cluster][Error][Signup][01][cluster_uid_generate]: Error during the signup process. Missing parameters!"
        send_to_logger("error", message, client_id=None, client_email=None)
        return "[Cluster][Error][Signup][01][cluster_uid_generate]: Error during the signup process. Missing parameters!"


def cluster_get_user_count():
    try:
        connection = mysql.connector.connect(
            host=__mysql_host__,
            database=__mysql_db__,
            user=__mysql_user__,
            password=__mysql_pass__
        )
        if connection.is_connected():
            # Here we have to execute the Query for adding new users to the DB
            cursor = connection.cursor()
            mysql_insert_query = "SELECT COUNT(*) FROM users;"
            cursor.execute(mysql_insert_query)
            query_result = cursor.fetchall()
            global __cluster_user_count__
            print("Experiment: ", query_result, " Type: ", type(query_result))
            __cluster_user_count__ = query_result
    except mysql.connector.Error as e:
        message = "[Cluster][Error][DB][01][cluster_get_user_count]: Error while starting the K8S MySQL Connection! Full error: [" + str(e) + "]."
        send_to_logger("error", message, client_id="None", client_email="None")
        # TODO: Send to the Logger
        print("[Cluster][DB][Err][01]: Error while starting the K8S MySQL Connection. Error: [", e, "].")
    finally:
        return True


if __name__ == "__main__":
    # Here we must use 127.0.0.1 as K8s doesn't seem to recognize localhost ....
    uvicorn.run(app, host='127.0.0.1', port=6900)
