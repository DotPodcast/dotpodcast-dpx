jQuery(document).ready(
    function($) {
        $('.waveform-player').each(
            function() {
                var self =  $(this);
                var height = self.data('height') || $(this).outerHeight(true);
                var wf = $('<div>').addClass('waveform').appendTo(self);
                var btn = $('<div>').addClass('player-button').appendTo(self);
                var url = self.data('src');
                var enabled = false;
                var wavesurfer = WaveSurfer.create(
                    {
                        backend: 'MediaElement',
                        container: wf.get(0),
                        height: 300,
                        waveColor: '#ffffff99',
                        progressColor: '#fff',
                        normalize: true
                    }
                );

                btn.on('click',
                    function() {
                        if(!enabled) {
                            return;
                        }

                        if(wavesurfer.isPlaying()) {
                            wavesurfer.pause();
                        } else {
                            wavesurfer.play();
                        }
                    }
                );

                wavesurfer.on('loading',
                    function() {
                        btn.addClass('loading');
                    }
                );

                wavesurfer.on('waveform-ready',
                    function() {
                        btn.removeClass('loading').addClass('paused');
                        enabled = true;
                    }
                );

                wavesurfer.on('play',
                    function() {
                        btn.removeClass('paused').addClass('playing');
                    }
                );

                wavesurfer.on('pause',
                    function() {
                        btn.removeClass('playing').addClass('paused');
                    }
                );

                wavesurfer.load(url);
            }
        );
    }
);
