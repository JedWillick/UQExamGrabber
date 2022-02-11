import sys
from typing import Union

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .env import Env


class UQDriver(Chrome):
    def __init__(self, env: Env, extra_args=None, extra_exp=None, **kwargs) -> None:
        super(UQDriver, self).__init__(
            options=self.default_options(env.headless, args=extra_args, exp=extra_exp),
            **kwargs
        )

        self.implicitly_wait(env.timeout)
        self.login(env.username, env.password)

    def login(self, username: str, password: str) -> None:
        self.get("https://auth.uq.edu.au/")

        self.find_element(By.ID, "username").send_keys(username)
        self.find_element(By.ID, "password").send_keys(password, Keys.RETURN)

        if self.current_url != "https://auth.uq.edu.au/idp/module.php/core/authenticate.php?as=uq":
            print("Failed to login!")
            sys.exit(1)

    @ staticmethod
    def default_options(headless: bool = True, args: Union[list, None] = None, exp: Union[dict, None] = None) -> ChromeOptions:
        opt = ChromeOptions()
        opt.add_argument('--headless') if headless else None
        opt.add_argument("--incognito")
        opt.add_experimental_option("excludeSwitches", ["enable-logging"])

        [opt.add_argument(arg) for arg in args] if args else None
        [opt.add_experimental_option(k, v)for k, v in exp.items()] if exp else None

        return opt
