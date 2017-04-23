require 'uri'
require 'open-uri'
HTML_DIR='html'
File.readlines('url.txt').each do |url|
  open(url.chomp, 'r') do |page|
    File.write(HTML_DIR + '/' + URI.parse(url.chomp).host, page.read)
  end
end
