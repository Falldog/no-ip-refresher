#!/usr/bin/env python3
import sys
import time
import requests
import subprocess
from os.path import join, exists, dirname, abspath
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# python2+3
try:
    import configparser
except:
    import ConfigParser as configparser

CUR_DIR = abspath(dirname(__file__))


class NoIpRefresher(object):
    def __init__(self, config):
        self.browser = webdriver.Firefox(log_path='/dev/null')
        self.wait = WebDriverWait(self.browser, 15)
        self.username = config.get('Refresher', 'username')
        self.password = config.get('Refresher', 'password')
        self.host = config.get('Refresher', 'host')
        self.ip = self.get_public_ip()

    def get_public_ip(self):
        resp = requests.get('http://ipinfo.io/ip')
        ip = resp.text.strip()
        print('public ip: %s' % ip)
        return ip

    def process(self):
        self.login()
        self.remove_exists_host()
        self.add_host()
        self.browser.quit()

    def login(self):
        print('try to login')
        self.browser.get('https://www.noip.com/login')
        time.sleep(2)

        elem = self.browser.find_element_by_css_selector('#clogs > input[name=username]')
        elem.clear()
        elem.send_keys(self.username)

        elem = self.browser.find_element_by_css_selector('#clogs > input[name=password]')
        elem.clear()
        elem.send_keys(self.password)

        elem = self.browser.find_element_by_css_selector('#clogs > button').click()

        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#main-navbar-collapse a.user-menu > i.fa-user')))
        print('login success!')

    def remove_exists_host(self):
        print('remove_exists_host')
        self.browser.get('https://my.noip.com/#!/dynamic-dns')
        time.sleep(2)

        elem = self.browser.find_element_by_css_selector('#host-panel > table')
        tbody = elem.find_element_by_tag_name('tbody')
        for tr in tbody.find_elements_by_tag_name('tr'):
            try:
                host = tr.find_element_by_css_selector('td[data-title="Host"] > a').text
                ip = tr.find_element_by_css_selector('td[data-title="IP / Target"]').text
                remove_btn = tr.find_element_by_css_selector('td.host-remove-col > div')
            except NoSuchElementException:
                continue

            print('exists host: %s, ip: %s' % (host, ip))

            if host == self.host:
                remove_btn.click()
                time.sleep(1)

                ok_btn = self.browser.find_element_by_css_selector('body > div.bootbox-confirm div.modal-footer > button.btn-primary')
                ok_btn.click()
                break

    def add_host(self):
        print('add_host')
        idx = self.host.index('.')
        domain_name = self.host[:idx]
        domain_suffix = self.host[idx+1:]

        self.browser.get('https://www.noip.com/members/dns/host.php')
        time.sleep(2)

        # domain name
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#hostname')))
        time.sleep(1)
        elem = self.browser.find_element_by_css_selector('#hostname')
        elem.clear()
        elem.send_keys(domain_name)

        # IP
        elem = self.browser.find_element_by_css_selector('#ip')
        elem.clear()
        elem.send_keys(self.ip)

        # domain suffix
        select = Select(self.browser.find_element_by_css_selector('select[name="host[domain]"]'))
        select.select_by_visible_text(domain_suffix)

        submit = self.browser.find_element_by_css_selector('input[type=submit]')
        self.browser.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()

        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#right-inner > div.successbox')))
        print('add host: %s success' % self.host)

    def add_host_new_design(self):
        print('add_host')
        idx = self.host.index('.')
        domain_name = self.host[:idx]
        domain_suffix = self.host[idx+1:]

        # self.browser.get('https://my.noip.com/#!/dynamic-dns')
        # time.sleep(2)

        add_host_btn = self.browser.find_element_by_css_selector('#host-panel > div.panel-footer > div > button')
        add_host_btn.click()

        # domain name
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#name')))
        time.sleep(1)
        elem = self.browser.find_element_by_css_selector('#name')
        elem.clear()
        elem.send_keys(domain_name)

        # IP
        elem = self.browser.find_element_by_css_selector('#host-modal .modal-body input[name=target]')
        elem.clear()
        elem.send_keys(self.ip)

        # domain suffix
        elem = self.browser.find_element_by_css_selector('#host-modal .modal-body select[name=domain] + div')
        elem.click()
        self.wait.until(EC.visibility_of(elem.find_element_by_css_selector('.chosen-search')))
        elem.send_keys(domain_suffix)
        time.sleep(1)
        elem.find_element_by_css_selector('.chosen-results .active-result').click()

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#host-modal div.modal-footer > button.btn-primary')))

        elem.send_keys(Keys.ENTER)


if __name__ == '__main__':
    config_file = join(CUR_DIR, 'refresher.cfg')
    if not exists(config_file):
        sys.exit("refresher.cfg doesn't exists")

    with open(config_file, 'r') as f:
        config = configparser.ConfigParser()
        config.readfp(f)
        refresher = NoIpRefresher(config)
        refresher.process()

