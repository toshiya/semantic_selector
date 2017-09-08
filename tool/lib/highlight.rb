module Highlight

  def load_highliter()
    script = 'var script = document.createElement("script"); script.type = "text/javascript"; script.src = "https://toshiya.github.io/semantic_selector/static/highlighter.min.js"; document.head.appendChild(script);'
    $driver.execute_script(script)

    sleep(2)

    script = 'window.myHighliter = new window.Highlighter({"color":"red"});'
    $driver.execute_script(script)
  end

  def highlight_by_name(name)
    script = <<SCRIPT
    var elements = document.getElementsByName(\"#{name}\");
    elements.forEach(function(element) {
      window.myHighliter.point(element);
      window.myHighliter.underline();
    })
SCRIPT
    $driver.execute_script(script)
  end

  def erase_by_name(name)
    script = <<SCRIPT
    var elements = document.getElementsByName(\"#{name}\");
    elements.forEach(function(element) {
      window.myHighliter.point(element);
      window.myHighliter.erase();
    })
SCRIPT
    $driver.execute_script(script)
  end

  module_function :load_highliter, :highlight_by_name, :erase_by_name
end
