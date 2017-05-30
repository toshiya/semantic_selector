require 'selenium-webdriver'
require 'active_record'
require 'pry'

class Input < ActiveRecord::Base
  self.table_name = 'inputs'
end

def db_setup
  ActiveRecord::Base.establish_connection(
    adapter: 'mysql2',
    host: 'localhost',
    username: 'root',
    password: '',
    database: 'register_form',
  )
end

def save(url, html, label)
  Input.create(
    url: url,
    html: html,
    label: label
  )
end

db_setup()
driver = Selenium::WebDriver.for :chrome

binding.pry

driver.quit
