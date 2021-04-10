$('.extra-fields-customer').click(function() {
  $('.customer_records').clone().appendTo('.customer_records_dynamic');
  $('.customer_records_dynamic .customer_records').addClass('single remove');
  $('.single .extra-fields-customer').remove();
  $('.single .d-flex').append('<div class="form-group"><a href="javascript:void(0)" class="remove-field btn-remove-customer btn btn-link btn-outline-danger mx-2 py-2"><i class="fas fa-minus"></i></a></div>');
  $('.customer_records_dynamic > .single').attr("class", "remove");

  $('.customer_records_dynamic input').each(function() {
    var count = 0;
    var fieldname = $(this).attr("name");
    $(this).attr('name', fieldname);
    count++;
  });

});

$(document).on('click', '.remove-field', function(e) {
  $(this).parent().parent('.d-flex').remove();
  e.preventDefault();
});
