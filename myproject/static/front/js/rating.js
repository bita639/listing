var $star_rating = $('.star .fa');


    var SetRatingStar = function() {
        return $star_rating.each(function() {


            if (parseInt($(this).siblings('.rating-value').val()) >= parseInt($(this).data('rating'))) {
                  return $(this).removeClass('fa-star-o').addClass('fa-star');
                } else {
                  return $(this).removeClass('fa-star').addClass('fa-star-o');
                }

            });

    };


    $(document).ready(function() {
        SetRatingStar();
    });
