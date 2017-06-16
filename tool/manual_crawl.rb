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
# Manual Labeling Command Example in Pry CLI
# $ driver.navigate.to "https://www.muji.net/store/cust/useradd/fullinfo?beforeUrl=terms"
# $ find_input_tags(driver)
# $ fill_input_tags(tags)
#
## 目視で番号の入ったラベルを確認しながら、ラベルを手動でつける
## 既存ラベル一覧
## https://github.dena.jp/gist/toshiya-komoda/87ebc5d16953ef07663869446570f63a
## 一覧にない場合は、都度新しいラベルを定義する
# $ save(driver, tags[2], "pc_email")

driver.quit
