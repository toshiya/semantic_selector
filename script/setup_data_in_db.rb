require 'uri'
require 'open-uri'
require 'oga'
require 'active_record'

class Input < ActiveRecord::Base
  self.table_name = 'inputs'
end

def db_setup
  ActiveRecord::Base.establish_connection(
    adapter: 'mysql2',
    host: 'localhost',
    username: 'root',
    password: 'root',
    database: 'login_form',
  )
end

def get_url_list
  url_list = []
  File.readlines('data/url.txt').each {|url| url_list.push(url.chomp) }
  return url_list
end

def save_inputs(url, document)
  document.xpath('//input').each do |input|
    type = input.attributes.find {|a| a.name == 'type'}
    next if type.nil? || type.value == 'hidden'
    begin
      Input.create(
        url: url,
        html: input.to_xml,
        label: 'other'
      )
    rescue => e
      puts e
    end
  end
end

def main
  db_setup()
  url_list = get_url_list()
  url_list.each do |url|
    begin
      html = open(url).read
      document = Oga.parse_html(html)
    rescue => e
      puts e
    end
    next if document.nil?

    save_inputs(url, document)
  end
end

main()
