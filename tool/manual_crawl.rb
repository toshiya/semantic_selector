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

def save(driver, node, label)
  url = driver.current_url
  html = node.attribute('outerHTML')
  parent_html = node.find_element(:xpath, "..").attribute('outerHTML')
  Input.create(
    url: url,
    html: html,
    parent_html: parent_html,
    label: label
  )
end

def find_input_tags(driver)
  driver.find_elements(:xpath, '//input[not(@type="hidden")]')
end

def find_radio_box(driver)
  driver.find_elements(:xpath, '//input[@type="radio"]')
end

def find_select_box(driver)
  driver.find_elements(:xpath, '//select[not(@type="hidden")]')
end

def find_check_box(driver)
  driver.find_elements(:xpath, '//input[@type="checkbox"]')
end

def fill_input_tags(input_tags)
  input_tags.each_with_index do |e, i|
    next unless e.displayed?
    begin
      e.send_keys i.to_s
    rescue => e
      puts e
    end
  end
end

db_setup()
driver = Selenium::WebDriver.for :chrome

binding.pry
driver.quit
