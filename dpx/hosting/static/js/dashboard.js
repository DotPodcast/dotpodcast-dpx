jQuery(document).ready(
    function($) {
        $('table input[type="checkbox"][name="select"]').on('click',
            function() {
                var input = $(this);
                var select = input.attr('value');
                var selected = input.is(':checked');
                var others = input.closest('table input[type="checkbox"][name="select"]').not('[value="all"]');

                switch(select) {
                    case 'all':
                        if(selected) {
                            others.removeAttr('checked');
                        } else {
                            others.attr('checked', 'checked');
                        }

                        break;
                }
            }
        );

        $('input[type="file"]').each(
            function() {
                var original = $(this);
                var container = original.parent();
                var input = $('<input>').attr(
                    'type', 'hidden'
                ).attr(
                    'name', original.attr('name')
                ).appendTo(container);

                var div = container.append('<div>');
                var accept = original.attr('accept');
                var uploader = new qq.FineUploader(
                    {
                        element: div.get(0),
                        validation: {
                            acceptFiles: accept
                        },
                        template: 'qq-template-' + (original.data('template') || 'button'),
                        chunking: {
                            enabled: true,
                            mandatory: true,
                            partSize: 1000000
                        },
                        request: {
                            endpoint: '/admin/upload/',
                            params: {
                                csrfmiddlewaretoken: input.closest('form').find(
                                    'input[name="csrfmiddlewaretoken"]'
                                ).val()
                            }
                        },
                        callbacks: {
                            onComplete: function(id, name, response, xhr) {
                                input.val(response.guid);
                            }
                        },
                        multiple: false
                    }
                );

                original.remove();
            }
        );

        $(':input[data-type="wysiwyg"]').markdownEditor(
            {
                fullscreen: false
            }
        );

        $(':input[data-slugify]').each(
            function() {
                var slugField = $(this);
                var form = slugField.closest('form');
                var sourceField = form.find(
                    ':input[name="' + slugField.data('slugify') + '"]'
                );

                if(slugField.val()) {
                    return;
                }

                sourceField.on('keypress',
                    function(e) {
                        setTimeout(
                            function() {
                                slugField.val(
                                    sourceField.val().toLowerCase().replace(
                                        /\s+/g, '-'
                                    ).replace(
                                        /[^\w\-]+/g, ''
                                    ).replace(
                                        /\-\-+/g, '-'
                                    ).replace(
                                        /^-+/, ''
                                    ).replace(
                                        /-+$/, ''
                                    )
                                );
                            },
                            10
                        );
                    }
                );
            }
        );
    }
);
