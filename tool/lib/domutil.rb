module DOMUtil
  def find_input_tags(driver)
    elements = driver.find_elements(:xpath, '//input[not(@type="hidden")]')
    elements.concat(driver.find_elements(:xpath, '//select[not(@type="hidden")]'))
  end

  module_function :find_input_tags
end
