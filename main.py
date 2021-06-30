import requests
import json
import mysql.connector

__master_url__ = "https://master.wpmt.tech"

__cluster_name__ = "cluster-eu01.wpmt.tech"
__cluster_url__ = "https://cluster-eu01.wpmt.tech"
__cluster_locale__ = "EU"
__cluster_user_count__ = 0

__mysql_host__ = None
__mysql_db__ = None
__mysql_user__ = None
__mysql_pass__ = None


def mysql_user_add(client_id, name, email, password, country, locale, notifications, news, ads):
    if None not in [__mysql_host__, __mysql_db__, __mysql_user__, __mysql_pass__]:
        try:
            connection = mysql.connector.connect(
                host=__mysql_host__,
                database=__mysql_db__,
                user=__mysql_user__,
                password=__mysql_pass__)
            if connection.is_connected():
                # Here we have to execute the Query for adding new users to the DB

                # TODO: Add logging for new user signups
                # These logs should contain the client_id and email
                print("[Cluster][DB][Info]: Added user [", client_id, "][", email, "].")
                pass
        except mysql.connector.Error as e:
            print("[Cluster][DB][Err][02]: Error while starting the MySQL Connection. Error: [", e, "].")
        finally:
            if connection.is_connected():
                connection.close()
    else:
        print("[Cluster][DB][Err][01]: Missing MySQL parameters. Source: [", client_id, "][", email, "].")


def cluster_key_generate():
    pass


def cluster_uid_generate(name, email, password, country, locale, notifications, news, ads):
    if None in [name, email, password, locale]:
        return "[Cluster][API][Err][01]: Missing parameters while singing up."
    # Get last user ID
    new_user_num = __cluster_user_count__ + 1
    generated_uid = __cluster_locale__ + "-UID-" + str(new_user_num).zfill(9)

    # Send the generated UID to the DB
    mysql_user_add(generated_uid, name, email, password, country, locale, notifications, news, ads)

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
        'name': name,
        'email': email,
        'password': password,
        'country': country,
        'locale': locale,
        'notifications': notifications,
        'news': news,
        'personalized_ads': ads
    }
    sent_request = requests.post(url, data=json.dumps(body), headers=headers)
    # End of sending to the Master DB


if __name__ == "__main__":
    result = cluster_uid_generate("Todor", "Email", "Pass", "US")
    print("UID: ", result)
