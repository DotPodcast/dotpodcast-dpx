jQuery(document).ready(
    function($) {
        $(document).on('click',
            '[data-action="dotpodcast.subscribe"]',
            function(e) {
                e.preventDefault();
                alert('Subscribe');
            }
        );
    }
);
