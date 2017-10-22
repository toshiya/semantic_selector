require 'readline'
require 'selenium-webdriver'
require 'colorize'
require_relative './lib/domutil'
require_relative './lib/dbutil'
require_relative './lib/highlight'
require_relative './lib/api_client'

LIST = [
  # available commands
  "load_page",
  "load_highliter",
  "collect",
  # common topics
  "mail_delivery",
  "pc_email",
  "gender",
  "password",
  "family_name",
  "first_name",
  "password_confirmation",
  "family_name_furigana",
  "first_name_furigana",
  "birthday_year",
  "birthday_month",
  "birthday_day",
  "address_town",
  "address_building",
  "address_street",
  "pc_email_confirmation",
  "phone_number",
  "prefecture",
  "phone_number_first",
  "phone_number_middle",
  "phone_number_last",
  "postal_code",
  "job",
  "postal_code_first",
  "postal_code_last",
  "entry_path",
  "questionnaire",
  "service_term",
  "user_id",
  "company_name",
  "user_type",
  "company_department",
  "other",
]

comp = proc { |s| LIST.grep(/^#{Regexp.escape(s)}/) }
Readline.completion_append_character = " "
Readline.completion_proc = comp

def put_q(msg)
  puts msg.green
end

def put_w(msg)
  puts msg.red
end

def put_n(msg)
  puts msg.blue
end

lambda {
  Kernel.module_eval do
    define_method :load_page do |url|
      $driver.get(url)
      if DBUtil.visited?($driver.current_url)
        put_w "[WARN] this page has already been visited? continue?"
      end

      Highlight.load_highliter()
    end

    define_method :load_highliter do
      Highlight.load_highliter()
    end

    # Interactive Shell based on inference
    define_method :collect do |start_index=0|
      start_index ||= 0
      tags = DOMUtil.find_input_tags($driver)

      put_n "total: #{tags.length} input fields found"

      tags.each_with_index do |tag, index|
        if start_index > index
          next
        end

        name = tag.attribute('name')
        html = tag.attribute('outerHTML')
        infered_topic = $api_client.inference_html(html)
        Highlight.highlight_by_name(name)

        put_n "#{index}/#{tags.length}"
        put_n "HTML"
        put_n html
        put_w "topic: #{infered_topic}.".red
        put_q "OK ? then press [enter]. or Input correct topic and [enter]"

        existing_topics = DBUtil.topics() || []
        prompt = Readline.readline('> ', true).strip
        while prompt.length > 0
          case prompt
          when "exit"
            return
          when "s","skip"
            infered_topic = "skip"
            break
          when "t", "topics"
            put_n "...listing all lables"
            existing_topics.each do |topic|
              put_n topic
            end
            put_q "input new topic"
            prompt = Readline.readline('> ', true).strip
            next
          else
            infered_topic = prompt
            unless existing_topics.include?(infered_topic)
              put_w "[WARN] This topic is not in the current DB."
              put_q "OK? if not, press [n]"
              answer = Readline.readline('> ', true).strip
              unless ["", "y", "yes"].include?(answer)
                put_q "input new topic"
                prompt = Readline.readline('> ', true).strip
                next
              end
            end
            break
          end
        end

        if infered_topic == "skip"
          Highlight.erase_by_name(name)
          put_n "...skiped"
          put_n ""
          next
        end

        put_n "new_topic: #{infered_topic}".blue
        Highlight.erase_by_name(name)
        DBUtil.save($driver, tag, infered_topic)
        put_n "...saved"
        put_n ""
      end

      put_n "...finsihed"
      puts
    end

    # show recorded tags for the current page
    define_method :show do
    end

    # edit a label of the record at the given index
    define_method :edit do |index|
    end
  end

}.call

DBUtil.db_setup()
$driver = Selenium::WebDriver.for :chrome
$api_client = ApiClient.new()

while cmd = Readline.readline('> ', true).strip
  put_n cmd
  begin
    eval(cmd)
  rescue => e
    put_w "[error] fail"
    put_w e.to_s.red
  end
end

$driver.quit
