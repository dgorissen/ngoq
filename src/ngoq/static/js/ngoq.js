$(function(){
  
  $("a[rel=popover]")
    .popover({
      offset: 10,
      html:true,
      // placement:'below', 
      content: function(){
        var table = $('<table>');
        
        $.each($(this).data('json'), function(key){
          var tr = $('<tr>');
          
          $('<th>').text(key).appendTo(tr);
          $('<td>').text(''+this).appendTo(tr);
          
          table.append(tr)
        })
        
        return table.html();
      },
      trigger: 'manual',
      title: function(){
        return $(this).text();
      },
    })
    .click(function(e) {
      e.preventDefault()
      
      $('.popover').remove();
      
      var $this = $(this);
      $.getJSON($this.attr('href'))
        .done(function(json){
          $this.data('json', json)
            .popover('show');
        })
      
    })
  
  // hide popovers when clicked
  $('.popover').live('click', function(){
    $(this).remove();
  })
    
    
  $('input[type=checkbox]').change(function(){
    var disable = !$(this).is(':checked');
    
    $(this)
      .closest('tr').toggleClass('disabled', disable)
      .find('input[type=input]').toggleClass('disabled', disable)
        .attr('disabled', disable ? 'disabled': false)
  
  })

})