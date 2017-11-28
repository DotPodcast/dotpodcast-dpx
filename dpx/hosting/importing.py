from .exceptions import ImportingError, ImportingHTTPError
from .settings import DOTPODCAST_DOMAIN


IMPORTERS = (
    'dotpodcast.host.importers.wp.WordPressImporter',
    'dotpodcast.host.importers.rss.RssAsHtmlImporter',
    'dotpodcast.host.importers.rss.RssImporter'
)

CATEGORY_TERMS = {
    'Arts': 'https://%s/taxonomies/subject/#art' % DOTPODCAST_DOMAIN,
    'Arts : Design': 'https://%s/taxonomies/subject/#design' % DOTPODCAST_DOMAIN,
    'Arts : Fashion & Beauty': 'https://%s/taxonomies/subject/#beauty' % DOTPODCAST_DOMAIN,
    'Arts : Fashion & Beauty': 'https://%s/taxonomies/subject/#fashion' % DOTPODCAST_DOMAIN,
    'Arts : Food': 'https://%s/taxonomies/subject/#food' % DOTPODCAST_DOMAIN,
    'Arts : Literature': 'https://%s/taxonomies/subject/#literature' % DOTPODCAST_DOMAIN,
    'Arts : Performing arts': 'https://%s/taxonomies/subject/#performing-arts' % DOTPODCAST_DOMAIN,
    'Arts : Visual Arts': 'https://%s/taxonomies/subject/#visual-arts' % DOTPODCAST_DOMAIN,

    'Business': 'https://%s/taxonomies/subject/#business' % DOTPODCAST_DOMAIN,
    'Business : Business News': 'https://%s/taxonomies/subject/#business-news' % DOTPODCAST_DOMAIN,
    'Business : Careers': 'https://%s/taxonomies/subject/#careers' % DOTPODCAST_DOMAIN,
    'Business : Investing': 'https://%s/taxonomies/subject/#investing' % DOTPODCAST_DOMAIN,
    'Business : Management & Marketing': 'https://%s/taxonomies/subject/#management' % DOTPODCAST_DOMAIN,
    'Business : Management & Marketing': 'https://%s/taxonomies/subject/#marketing' % DOTPODCAST_DOMAIN,
    'Business : Shopping': 'https://%s/taxonomies/subject/#retail' % DOTPODCAST_DOMAIN,

    'Comedy': 'https://%s/taxonomies/subject/#comedy' % DOTPODCAST_DOMAIN,

    'Communication': 'https://%s/taxonomies/subject/#communication' % DOTPODCAST_DOMAIN,
    'Communication : Film': 'https://%s/taxonomies/subject/#film' % DOTPODCAST_DOMAIN,
    'Communication : Music': 'https://%s/taxonomies/subject/#music' % DOTPODCAST_DOMAIN,
    'Communication : TV': 'https://%s/taxonomies/subject/#tv' % DOTPODCAST_DOMAIN,

    'Education': 'https://%s/taxonomies/subject/#education' % DOTPODCAST_DOMAIN,
    'Education : Educational Technology': 'https://%s/taxonomies/subject/#educational-technology' % DOTPODCAST_DOMAIN,
    'Education : Higher Education': 'https://%s/taxonomies/subject/#further-education' % DOTPODCAST_DOMAIN,
    'Education : K-12': 'https://%s/taxonomies/subject/#primary-education' % DOTPODCAST_DOMAIN,
    'Education : Language Courses': 'https://%s/taxonomies/subject/#language-courses' % DOTPODCAST_DOMAIN,
    'Education : Training': 'https://%s/taxonomies/subject/#training' % DOTPODCAST_DOMAIN,

    'Games & Hobbies': 'https://%s/taxonomies/subject/#games' % DOTPODCAST_DOMAIN,
    'Games & Hobbies : Video Games': 'https://%s/taxonomies/subject/#video-games' % DOTPODCAST_DOMAIN,

    'Government & Organizations': 'https://%s/taxonomies/subject/#governments-and-organizations' % DOTPODCAST_DOMAIN,
    'Government & Organizations : Local': 'https://%s/taxonomies/subject/#local-government' % DOTPODCAST_DOMAIN,
    'Government & Organizations : National': 'https://%s/taxonomies/subject/#national-government' % DOTPODCAST_DOMAIN,
    'Government & Organizations : Non-Profit': 'https://%s/taxonomies/subject/#non-profit-organizations' % DOTPODCAST_DOMAIN,
    'Government & Organizations : Regional': 'https://%s/taxonomies/subject/#regional-organizations' % DOTPODCAST_DOMAIN,

    'Health': 'https://%s/taxonomies/subject/#health' % DOTPODCAST_DOMAIN,
    'Health : Alternative Health': 'https://%s/taxonomies/subject/#alternative-health' % DOTPODCAST_DOMAIN,
    'Health : Fitness & Nutrition': 'https://%s/taxonomies/subject/#fitness' % DOTPODCAST_DOMAIN,
    'Health : Fitness & Nutrition': 'https://%s/taxonomies/subject/#nutrition' % DOTPODCAST_DOMAIN,
    'Health : Self-Help': 'https://%s/taxonomies/subject/#self-help' % DOTPODCAST_DOMAIN,

    'News & Politics': 'https://%s/taxonomies/subject/#news' % DOTPODCAST_DOMAIN,

    'Science & Medicine': 'https://%s/taxonomies/subject/#science' % DOTPODCAST_DOMAIN,
    'Science & Medicine : Medicine': 'https://%s/taxonomies/subject/#medicine' % DOTPODCAST_DOMAIN,
    'Science & Medicine : Natural Sciences': 'https://%s/taxonomies/subject/#natural-sciences' % DOTPODCAST_DOMAIN,
    'Science & Medicine : Social Sciences': 'https://%s/taxonomies/subject/#social-sciences' % DOTPODCAST_DOMAIN,

    'Society & Culture': 'https://%s/taxonomies/subject/#society-and-culture' % DOTPODCAST_DOMAIN,
    'Society & Culture : History': 'https://%s/taxonomies/subject/#history' % DOTPODCAST_DOMAIN,
    'Society & Culture : Personal Journals': 'https://%s/taxonomies/subject/#personal-journals' % DOTPODCAST_DOMAIN,
    'Society & Culture : Philosophy': 'https://%s/taxonomies/subject/#philosophy' % DOTPODCAST_DOMAIN,
    'Society & Culture : Places & Travel': 'https://%s/taxonomies/subject/#places-and-travel' % DOTPODCAST_DOMAIN,

    'Sports & Recreation': 'https://%s/taxonomies/subject/#sport' % DOTPODCAST_DOMAIN,
    'Sports & Recreation : Amateur': 'https://%s/taxonomies/subject/#amateur-sport' % DOTPODCAST_DOMAIN,
    'Sports & Recreation : College & High School': 'https://%s/taxonomies/subject/#college-and-high-school-sport' % DOTPODCAST_DOMAIN,
    'Sports & Recreation : Outdoor': 'https://%s/taxonomies/subject/#outdoor-sport' % DOTPODCAST_DOMAIN,
    'Sports & Recreation : Professional': 'https://%s/taxonomies/subject/#professional-sport' % DOTPODCAST_DOMAIN,

    'Technology': 'https://%s/taxonomies/subject/#technology' % DOTPODCAST_DOMAIN,
    'Technology : Gadgets': 'https://%s/taxonomies/subject/#gadgets' % DOTPODCAST_DOMAIN,
    'Technology : Podcasting': 'https://%s/taxonomies/subject/#podcasting' % DOTPODCAST_DOMAIN,
    'Technology : Software How-To': 'https://%s/taxonomies/subject/#software-how-to' % DOTPODCAST_DOMAIN,
    'Technology : Tech News': 'https://%s/taxonomies/subject/#technology-news' % DOTPODCAST_DOMAIN
}

LANGUAGE_TERM_TEMPLATE = 'https://%s/taxonomies/language/#%%s' % DOTPODCAST_DOMAIN
PROFANITY_TERM_TEMPLATE = 'https://%s/taxonomies/profanity/#%%s' % DOTPODCAST_DOMAIN


def get_importer(name):
    from importlib import import_module

    module, klass = name.rsplit('.', 1)
    module = import_module(module)
    klass = getattr(module, klass)
    return klass()


def download_file(url, as_django_file=False):
    from tempfile import mkstemp
    from os import write, close
    from mimetypes import guess_extension
    import requests

    response = requests.get(
        url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) '
                'AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 '
                'Mobile/14A300 Safari/602.1'
            )
        },
        stream=True
    )

    ext = guess_extension(response.headers['Content-Type'])
    handle, filename = mkstemp(suffix=ext)

    response.raise_for_status()
    for chunk in response.iter_content(chunk_size=1024):
        write(handle, chunk)

    close(handle)

    if as_django_file:
        from django.core.files import File
        return File(
            open(filename, 'rb')
        )

    return filename


def category_to_taxonomy_term(category):
    if isinstance(category, (list, tuple)):
        key = ' : '.join(category)
    else:
        key = category

    return CATEGORY_TERMS.get(key)


def import_feed(stream):
    for importer in IMPORTERS:
        stream.seek(0)
        importer = get_importer(importer)
        feed = importer.apply(
            stream.read()
        )

        if feed is None:
            continue

        metadata = importer.get_podcast_data(feed)
        language = metadata.get('language')
        explicit = metadata.get('explicit') != 'no'

        def get_taxonomy_terms():
            if language:
                yield LANGUAGE_TERM_TEMPLATE % language.replace('-', '_')

            yield PROFANITY_TERM_TEMPLATE % (
                explicit and 'moderate' or 'none'
            )

            for category in importer.get_categories(feed):
                if category:
                    term = category_to_taxonomy_term(category)
                    if term:
                        yield term


        return dict(
            taxonomy_terms=get_taxonomy_terms(),
            items=[
                importer.get_item_data(feed, item)
                for item in importer.get_items(feed)
            ],
            **metadata
        )

    raise ImportingError('No importer could process the source feed.')


def get_feed_stream(url):
    from os import remove
    import requests

    try:
        filename = download_file(url)
    except requests.exceptions.HTTPError as ex:
        raise ImportingHTTPError(
            str(ex)
        )

    try:
        return open(filename, 'r')
    finally:
        remove(filename)
