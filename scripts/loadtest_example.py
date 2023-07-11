from locust import HttpUser, task, tag, LoadTestShape, constant
import json

class Constant_RPS(LoadTestShape):
    initial_user = 1
    max_users = 10
    target_rps = 10
    spawn_rate = 2
    test_duration = 10  # in seconds

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.test_duration:   # test_duration in seconds
            return (self.target_rps, self.max_users)
        else:
            return None
    
    def user_count(self, user_count):
        if user_count < self.initial_user:
            return self.initial_user
        else:
            achieved_rps = self.get_shape()[0]
            if achieved_rps < self.target_rps:
                additional_user = int((self.target_rps - achieved_rps) / self.spawn_rate)
                return min(user_count + additional_user, self.max_users)
            else:
                return user_count
            
    def get_wait_time(self):
        achieved_rps = self.get_shape()[0]
        if achieved_rps > 0:
            return 1 / achieved_rps
        else:
            return 0
            
class Traffic_Shape(Constant_RPS):
    pass

class Testing_Example(HttpUser):
    # wait_time =  between(1, 3)

    @tag("get_users")
    @task(1)
    def get_users(self): 
        with self.client.get("/api/users?page=2", catch_response=True) as response:
            parsed_response = None

            try:
                parsed_response = json.loads(response.content.decode("utf-8"))
            except ValueError:
                if parsed_response is None:
                    parsed_response = { "page": "" }
                print("Response is not a JSON")
                print(response.content.decode("utf-8"))

            if parsed_response["page"] == 2 and response.status_code == 200:
                response.success()
            else:
                error_msg = None
                if response.status_code != 200:
                    error_msg = "HTTP Response: " + str(response.status_code) + " | Body Content: " + response.content.decode("utf-8")
                else:
                    error_msg = response.content.decode("utf-8")
                response.failure(error_msg)

    @tag("post_login")
    @task(2)
    def post_login(self):
        payload = {
            "email": "eve.holt@reqres.in",
	        "password": "cityslicka"
        }

        header = {
            "Content-Type": "application/json"
        }

        with self.client.post("/api/login", json=payload, headers=header, catch_response=True) as response:
            parsed_response = None

            try:
                parsed_response = json.loads(response.content.decode("utf-8"))
            except ValueError:
                if parsed_response is None:
                    parsed_response = { "token": "" }
                print("Response is not a JSON")
                print(response.content.decode("utf-8"))

            if parsed_response["token"] == "QpwL5tke4Pnpja7X4" and response.status_code == 200:
                response.success()
            else:
                error_msg = None
                if response.status_code != 200:
                    error_msg = "HTTP Response: " + str(response.status_code) + " | Body Content: " + response.content.decode("utf-8")
                else:
                    error_msg = response.content.decode("utf-8")
                response.failure(error_msg)

if __name__ == "__main__":
    Testing_Example.run(
        shape=Traffic_Shape(),
        user_spawn_rate=constant(1)
    )