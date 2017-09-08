require 'selenium-webdriver'
require 'active_record'
require 'pry'
require_relative './lib/domutil'
require_relative './lib/dbutil'
require_relative './lib/highlight'

lambda {
  Kernel.module_eval do
    define_method :load_page do |url|
      $driver.get(url)
      if DBUtil.visited?($driver.current_url)
        puts "[WARN] this page has already been visited? continue?"
      end

      Highlight.load_highliter()
    end

    # Interactive Shell based on inference
    define_method :collect do
      tags = DOMUtil.find_input_tags($driver)

      tags.each do |tag|
        existing_labels = DBUtil.labels() || []
        name = tag.attribute('name')
        Highlight.highlight_by_name(name)

        puts "HTML"
        puts tag.attribute('outerHTML')
        infered_label = "pc_email"
        puts "LABEL: #{infered_label}, is it OK? or Input correct label"

        prompt = STDIN.gets.chomp.downcase
        while prompt.length > 0
          case prompt
          when "labels"
            puts "...listing all lables"
            puts existing_labels
            puts "input new label"
            prompt = STDIN.gets.chomp.downcase
            next
          else
            new_label = prompt
            unless existing_labels.include?(new_label)
              puts "this is new label. is it OK ? if not, press [n]"
              answer = STDIN.gets.chomp.downcase
              unless ["", "y", "yes"].include?(answer)
                puts "input new label"
                prompt = STDIN.gets.chomp.downcase
                next
              end
            end
            infered_label = new_label
            puts "new_label: #{infered_label}"
            break
          end
        end

        Highlight.erase_by_name(name)
        DBUtil.save($driver.current_url, tag, infered_label)
        puts "...saved"
        puts
      end

      puts "...labeling finsihed"
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

binding.pry

$driver.quit
