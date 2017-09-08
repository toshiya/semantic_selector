module DOMUtil
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

  module_function :find_input_tags, :find_radio_box, :find_select_box, :find_check_box
end
