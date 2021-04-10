jQuery(document).ready(function($) {
    $("a.delete-listing-image").confirm({
        content: "Ligting Image will be deleted"
    });
    $("a.delete-listing-image").confirm({
        buttons: {
            hey: function() {
                location.href = this.$target.attr("href");
            }
        }
    });

    $("a.delete-listing-extra").confirm({
        content: "Ligting extra will be deleted"
    });
    $("a.delete-listing-extra").confirm({
        buttons: {
            hey: function() {
                location.href = this.$target.attr("href");
            }
        }
    });

    $("a.listing-inactive").confirm({
        content: "Listing will be inactivated"
    });
    $("a.listing-inactive").confirm({
        buttons: {
            hey: function() {
                location.href = this.$target.attr("href");
            }
        }
    });


    $("a.listing-active").confirm({
        content: "Listing will be activated"
    });
    $("a.listing-active").confirm({
        buttons: {
            hey: function() {
                location.href = this.$target.attr("href");
            }
        }
    });

    $("a.listing-delete").confirm({
        content: "Listing will be Deleted"
    });
    $("a.listing-delete").confirm({
        buttons: {
            hey: function() {
                location.href = this.$target.attr("href");
            }
        }
    });
});
