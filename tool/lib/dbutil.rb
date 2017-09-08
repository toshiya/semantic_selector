require_relative './domutil'
require 'active_record'
ActiveRecord::Base.default_timezone = :local
class Input < ActiveRecord::Base
  self.table_name = 'test_inputs'
end

module DBUtil
  def db_setup
    ActiveRecord::Base.establish_connection(
      adapter: 'mysql2',
      host: 'localhost',
      username: 'root', password: '',
      database: 'register_form',
    )
  end

  def save(driver, tag, label)
    url = driver.current_url
    html = tag.attribute('outerHTML')
    parent_html = tag.find_element(:xpath, "..").attribute('outerHTML')
    label_html = nil
    dom_id = tag.attribute('id')
    if dom_id
      label_elements = DOMUtil.find_labels_by_id(dom_id)
      if label_elements.length > 0
        label_html = label_elements[0].attribute("outerHTML")
      end
    end

    Input.create(
      url: url,
      html: html,
      parent_html: parent_html,
      label_html: label_html,
      label: label,
    )
  end

  def labels()
    Input.select('label').group('label').map(&:label)
  end

  def urls()
    Input.select('url').group('url').map(&:url)
  end

  def visited?(current_url)
    urls.map{ |a| a.split('?')[0] }.include?(current_url.split('?')[0])
  end

  module_function :db_setup, :save, :labels, :urls, :visited?
end
