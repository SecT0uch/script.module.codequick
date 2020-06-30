import unittest

from codequick import listing, route, resolver
from codequick.support import dispatcher
from codequick.utils import unicode_type
import xbmcgui
import pickle
import xbmc
import sys

PY3 = sys.version_info >= (3, 0)


class TestGlobalLocalization(unittest.TestCase):
    def test_next_page(self):
        ret = xbmc.getLocalizedString(listing.NEXT_PAGE)
        self.assertEqual(ret, "Next page")

    def test_search(self):
        ret = xbmc.getLocalizedString(listing.SEARCH)
        self.assertEqual(ret, "Search")


class Params(unittest.TestCase):
    def setUp(self):
        self.base = listing.Params()

    def tearDown(self):
        self.base = None

    def test_get_and_set(self):
        self.base["test"] = "data"
        self.assertIn("test", self.base)
        ret = self.base["test"]
        self.assertIsInstance(ret, unicode_type)
        self.assertEqual(ret, "data")

    def test_get_fail(self):
        with self.assertRaises(KeyError):
            _ = self.base["test"]

    def test_deleter(self):
        self.base["test"] = "data"
        self.assertIn("test", self.base)
        del self.base["test"]
        self.assertNotIn("test", self.base)

    def test_deleter_fail(self):
        with self.assertRaises(KeyError):
            del self.base["test"]

    def test_len(self):
        self.base["test1"] = "one"
        self.base["test2"] = "two"
        self.assertEqual(len(self.base), 2)

    def test_iter(self):
        self.base["test1"] = "data"
        self.base["test2"] = "data"
        self.assertListEqual(list(self.base), ["test1", "test2"])


class Art(Params):
    def setUp(self):
        self.listitem = xbmcgui.ListItem()
        self.base = listing.Art()

    def test_empty_setter(self):
        self.base["test"] = ""
        self.assertIn("test", self.base)
        self.base.clean()
        self.assertNotIn("test", self.base)

    def test_local_thumb(self):
        self.base.local_thumb("image.jpg")
        self.assertIn("thumb", self.base)

    def test_global_thumb(self):
        self.base.global_thumb("recent.png")
        self.assertIn("thumb", self.base)

    def test_close_without_extras(self):
        listing.fanart = "fanart"
        self.assertNotIn("thumb", self.base)
        self.assertNotIn("fanart", self.base)
        self.assertNotIn("icon", self.base)
        self.base._close(self.listitem, False)
        self.assertIn("thumb", self.base)
        self.assertIn("fanart", self.base)
        self.assertIn("icon", self.base)

    def test_close_with_extras(self):
        listing.fanart = "fanart"
        self.base["thumb"] = ""
        self.base["icon"] = ""
        self.base._close(self.listitem, False)
        self.assertNotIn("icon", self.base)
        self.assertNotIn("thumb", self.base)
        self.assertIn("fanart", self.base)


class Info(Params):
    def setUp(self):
        self.listitem = xbmcgui.ListItem()
        self.base = listing.Info()

    def test_empty_setter(self):
        self.base["test"] = ""
        self.assertNotIn("test", self.base)

    def test_duration_seconds_int(self):
        self.base["duration"] = 330
        self.assertIsInstance(self.base["duration"], int)
        self.assertEqual(self.base["duration"], 330)

    def test_duration_seconds_str(self):
        self.base["duration"] = "330"
        self.assertIsInstance(self.base["duration"], int)
        self.assertEqual(self.base["duration"], 330)

    def test_duration_time(self):
        self.base["duration"] = "5:30"
        self.assertIsInstance(self.base["duration"], int)
        self.assertEqual(self.base["duration"], 330)

    def test_duration_invalid(self):
        self.base["duration"] = ":5;30"
        self.assertIsInstance(self.base["duration"], int)
        self.assertEqual(self.base["duration"], 330)

    @unittest.skipIf(PY3, "Size is an long in python2")
    def test_size_py2(self):
        self.base["size"] = "256816"
        # noinspection PyUnresolvedReferences
        self.assertIsInstance(self.base["size"], long)

    @unittest.skipUnless(PY3, "Size is an int in python3")
    def test_size_py3(self):
        self.base["size"] = "256816"
        self.assertIsInstance(self.base["size"], int)

    def test_size_invalid(self):
        with self.assertRaises(TypeError):
            self.base["size"] = "s256816"

    def test_genre_str(self):
        self.base["genre"] = "Science Fiction"
        self.assertIsInstance(self.base["genre"], unicode_type)

    def test_genre_bytes(self):
        self.base["genre"] = b"Science Fiction"
        self.assertIsInstance(self.base["genre"], unicode_type)

    def test_genre_uni(self):
        self.base["genre"] = u"Science Fiction"
        self.assertIsInstance(self.base["genre"], unicode_type)

    def test_genre_int(self):
        self.base["genre"] = 11100010
        self.assertIsInstance(self.base["genre"], int)

    def test_date(self):
        self.base.date("june 27, 2017", "%B %d, %Y")
        self.assertEqual(self.base["date"], "27.06.2017")
        self.assertEqual(self.base["aired"], "2017-06-27")
        self.assertEqual(self.base["year"], "2017")

    def test_close(self):
        self.base["plot"] = "plot"
        self.base._close(self.listitem, "video")


class Property(Params):
    def setUp(self):
        self.listitem = xbmcgui.ListItem()
        self.base = listing.Property()

    def test_close(self):
        self.base["StartOffset"] = "256.4"
        self.base._close(self.listitem)

    def test_empty_setter(self):
        self.base["test"] = ""
        self.assertNotIn("test", self.base)


class Stream(Params):
    def setUp(self):
        self.listitem = xbmcgui.ListItem()
        self.base = listing.Stream()

    def test_empty_setter(self):
        self.base["test"] = ""
        self.assertNotIn("test", self.base)

    def test_required_type(self):
        with self.assertRaises(TypeError):
            self.base["channels"] = "two"

    def test_hd_false(self):
        self.base.hd(False)
        self.assertEqual(self.base["width"], 768)
        self.assertEqual(self.base["height"], 576)
        self.assertNotIn("aspect", self.base)

    def test_hd_zero(self):
        self.base.hd(0)
        self.assertEqual(self.base["width"], 768)
        self.assertEqual(self.base["height"], 576)
        self.assertNotIn("aspect", self.base)

    def test_hd_True(self):
        self.base.hd(True)
        self.assertEqual(self.base["width"], 1280)
        self.assertEqual(self.base["height"], 720)
        self.assertIn("aspect", self.base)
        self.assertEqual(self.base["aspect"], 1.78)

    def test_hd_one(self):
        self.base.hd(1)
        self.assertEqual(self.base["width"], 1280)
        self.assertEqual(self.base["height"], 720)
        self.assertIn("aspect", self.base)
        self.assertEqual(self.base["aspect"], 1.78)

    def test_hd_fullhd(self):
        self.base.hd(2)
        self.assertEqual(self.base["width"], 1920)
        self.assertEqual(self.base["height"], 1080)
        self.assertIn("aspect", self.base)
        self.assertEqual(self.base["aspect"], 1.78)

    def test_hd_ultrahd(self):
        self.base.hd(3)
        self.assertEqual(self.base["width"], 3840)
        self.assertEqual(self.base["height"], 2160)
        self.assertIn("aspect", self.base)
        self.assertEqual(self.base["aspect"], 1.78)

    def test_hd_aspect(self):
        self.base.hd(1, aspect=1.33)  # 4:3
        self.assertEqual(self.base["width"], 1280)
        self.assertEqual(self.base["height"], 720)
        self.assertIn("aspect", self.base)
        self.assertEqual(self.base["aspect"], 1.33)

    def test_hd_invalid(self):
        with self.assertRaises(ValueError):
            self.base.hd(5)

    def test_unknown(self):
        self.base.hd(None)
        self.assertNotIn("width", self.base)
        self.assertNotIn("height", self.base)
        self.assertNotIn("aspect", self.base)

    def test_close(self):
        self.base["video_codec"] = "h265"
        self.base["audio_language"] = "en"
        self.base["subtitle_language"] = "en"
        self.base._close(self.listitem)

    def test_close_invalid(self):
        self.base["subtitle_languages"] = "en"
        with self.assertRaises(KeyError):
            self.base._close(self.listitem)


class Context(unittest.TestCase):
    def setUp(self):
        self.listitem = xbmcgui.ListItem()
        self.base = listing.Context()
        self.org_routes = dispatcher.registered_routes.copy()

        # noinspection PyUnusedLocal
        @route.Route.register
        def test_callback(_, test):
            pass

        # noinspection PyUnusedLocal
        @route.Route.register
        def root(_):
            pass

        self.test_callback = test_callback

    def tearDown(self):
        dispatcher.reset()
        dispatcher.registered_routes.clear()
        dispatcher.registered_routes.update(self.org_routes)

    def test_container(self):
        self.base.container(self.test_callback, "test label")
        label, command = self.base[0]

        self.assertEqual(label, "test label")
        self.assertEqual(command, "XBMC.Container.Update(plugin://script.module.codequick/"
                                  "tests/test_listing/test_callback)")

    def test_container_with_params(self):
        self.base.container(self.test_callback, "test label", True, url="tester")
        label, command = self.base[0]

        self.assertEqual(label, "test label")
        self.assertTrue(command.startswith("XBMC.Container.Update(plugin://script.module.codequick/"
                                           "tests/test_listing/test_callback?_pickle_="))

    def test_script(self):
        self.base.script(self.test_callback, "test label")
        label, command = self.base[0]

        self.assertEqual(label, "test label")
        self.assertEqual(command, "XBMC.RunPlugin(plugin://script.module.codequick/"
                                  "tests/test_listing/test_callback)")

    def test_script_with_params(self):
        self.base.script(self.test_callback, "test label", True, url="tester")
        label, command = self.base[0]

        self.assertEqual(label, "test label")
        self.assertTrue(command.startswith("XBMC.RunPlugin(plugin://script.module.codequick/"
                                           "tests/test_listing/test_callback?_pickle_="))

    @unittest.skipIf(PY3, "only work under python 2")
    def test_related_py2(self):
        self.base.related(self.test_callback)
        label, command = self.base[0]

        self.assertEqual(label, "Related Videos")
        self.assertEqual(command, "XBMC.Container.Update(plugin://script.module.codequick/tests/test_listing/"
                                  "test_callback?_pickle_=80027d710055075f7469746c655f7101580e00000052656c61"
                                  "74656420566964656f737102732e)")

    @unittest.skipUnless(PY3, "only work under python 3")
    def test_related_py3(self):
        self.base.related(self.test_callback)
        label, command = self.base[0]

        self.assertEqual(label, "Related Videos")
        self.assertEqual(command, "XBMC.Container.Update(plugin://script.module.codequick/tests/test_listing/"
                                  "test_callback?_pickle_=8004951f000000000000007d948c075f746974"
                                  "6c655f948c0e52656c6174656420566964656f7394732e)")

    def test_related_with_params(self):
        self.base.related(self.test_callback, test=True)
        label, command = self.base[0]

        self.assertEqual(label, "Related Videos")
        self.assertTrue(command.startswith("XBMC.Container.Update(plugin://script.module.codequick/"
                                           "tests/test_listing/test_callback?_pickle_="))

    def test_close(self):
        self.base.related(self.test_callback)
        self.base._close(self.listitem)


class TestListitem(unittest.TestCase):
    def setUp(self):
        self.listitem = listing.Listitem()
        self.org_routes = dispatcher.registered_routes.copy()

        # noinspection PyUnusedLocal
        @route.Route.register
        def route_callback(_, data=None):
            pass

        # noinspection PyUnusedLocal
        @route.Route.register
        def route_callback_args(_, test, full=False):
            pass

        @resolver.Resolver.register
        def resolver_callback(_):
            pass

        self.route_callback = route_callback
        self.route_callback_args = route_callback_args
        self.resolver_callback = resolver_callback

    def tearDown(self):
        dispatcher.reset()
        dispatcher.registered_routes.clear()
        dispatcher.registered_routes.update(self.org_routes)

    def test_label(self):
        self.listitem.label = "test label"
        self.assertIsInstance(self.listitem.label, unicode_type)
        self.assertEqual(self.listitem.label, u"test label")
        self.assertIn("_title_", self.listitem.params)
        self.assertIn("title", self.listitem.info)

    def test_unformatted_label(self):
        self.listitem.label = "[B]test label[/B]"
        self.assertEqual(self.listitem.info["title"], u"test label")

    def test_callback(self):
        self.listitem.set_callback(self.route_callback)
        self.assertEqual(self.listitem.path, self.route_callback.route)

    def test_callback_args(self):
        self.listitem.set_callback(self.route_callback_args, "yes", full=True)
        self.assertEqual(self.listitem.path, self.route_callback_args.route)
        self.assertTupleEqual(self.listitem._args, ("yes",))
        self.assertIn("full", self.listitem.params)

    def test_close_route(self):
        self.listitem.set_callback(self.route_callback)
        path, raw_listitem, isfolder = self.listitem._close()
        self.assertEqual(path, "plugin://script.module.codequick/tests/test_listing/route_callback")
        self.assertTrue(isfolder)

    def test_close_no_callback(self):
        path, raw_listitem, isfolder = self.listitem._close()
        self.assertEqual(path, "")
        self.assertFalse(isfolder)

    def test_close_route_params(self):
        self.listitem.set_callback(self.route_callback, "yes", full=True)
        path, raw_listitem, isfolder = self.listitem._close()
        self.assertTrue(path.startswith("plugin://script.module.codequick/tests/test_listing/route_callback?_pickle_="))
        self.assertTrue(isfolder)

    def test_close_resolver(self):
        self.listitem.set_callback(self.resolver_callback)
        path, raw_listitem, isfolder = self.listitem._close()
        self.assertEqual(path, "plugin://script.module.codequick/tests/test_listing/resolver_callback")
        self.assertFalse(isfolder)

    def test_close_url(self):
        self.listitem.set_path("http://example.com/video.mkv")
        path, raw_listitem, isfolder = self.listitem._close()
        self.assertEqual(path, "http://example.com/video.mkv")
        self.assertFalse(isfolder)

    def test_close_subtitle(self):
        self.listitem.subtitles.append("http://path.to/subtitle")
        self.listitem.set_path("http://example.com/video.mkv")
        path, raw_listitem, isfolder = self.listitem._close()
        self.assertEqual(path, "http://example.com/video.mkv")
        self.assertFalse(isfolder)

    def test_from_dict(self):
        listitem = listing.Listitem.from_dict(self.route_callback, "test label",
                                              params={"test": True},
                                              info={"size": 135586565},
                                              art={"fanart": "fanart.jpg"},
                                              stream={"channels": 6},
                                              properties={"isfolder": "true"},
                                              context=[("related", "XBMC.Container.Update")])

        self.assertIsInstance(listitem, listing.Listitem)
        self.assertEqual(listitem.params["test"], True)
        self.assertEqual(listitem.info["size"], 135586565)
        self.assertEqual(listitem.art["fanart"], "fanart.jpg")
        self.assertEqual(listitem.stream["channels"], 6)
        self.assertEqual(listitem.property["isfolder"], "true")
        self.assertListEqual(listitem.context, [('related', 'XBMC.Container.Update')])

    def test_next_page(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def root(_, url):
            pass

        listitem = listing.Listitem.next_page("http://example.com/videos?page2")

        self.assertIsInstance(listitem, listing.Listitem)
        self.assertEqual(listitem.label, "[B]Next page 2[/B]")
        self.assertTrue(listitem.art["thumb"].endswith("next.png"))
        self.assertTupleEqual(listitem._args, ("http://example.com/videos?page2",))

    def test_youtube(self):
        listitem = listing.Listitem.youtube("UC4QZ_LsYcvcq7qOsOhpAX4A")
        self.assertIsInstance(listitem, listing.Listitem)
        self.assertEqual(listitem.params["contentid"], "UC4QZ_LsYcvcq7qOsOhpAX4A")
        self.assertTrue(listitem.art["thumb"].endswith("videos.png"))

    def test_recent_with_arg(self):
        listitem = listing.Listitem.recent(self.route_callback, "data", work=True)
        self.assertIsInstance(listitem, listing.Listitem)
        self.assertTrue(listitem.art["thumb"].endswith("recent.png"))
        self.assertIsInstance(listitem._args, tuple)
        self.assertIn("data", listitem._args)
        self.assertTrue(len(listitem._args) == 1)
        self.assertIn("work", listitem.params)
        self.assertTrue(listitem.params["work"] is True)

    def test_recent_without_arg(self):
        listitem = listing.Listitem.recent(self.route_callback)
        self.assertIsInstance(listitem, listing.Listitem)
        self.assertTrue(listitem.art["thumb"].endswith("recent.png"))
        self.assertIsInstance(listitem._args, tuple)
        self.assertTrue(len(listitem._args) == 0)

    def test_search_with_args(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def search_results(_, url="", search_query=""):
            pass

        listitem = listing.Listitem.search(search_results, "url", search_query="working")
        self.assertIsInstance(listitem, listing.Listitem)
        self.assertEqual(listitem.label, "[B]Search[/B]")
        self.assertTrue(listitem.art["thumb"].endswith("search.png"))

    def test_search_without_args(self):
        # noinspection PyUnusedLocal
        @route.Route.register
        def search_results(_, url="", search_query=""):
            pass

        listitem = listing.Listitem.search(search_results)
        self.assertIsInstance(listitem, listing.Listitem)
        self.assertEqual(listitem.label, "[B]Search[/B]")
        self.assertTrue(listitem.art["thumb"].endswith("search.png"))
        self.assertIsInstance(listitem._args, tuple)
        self.assertTrue(len(listitem._args) == 0)

    def test_pickle(self):
        self.listitem.info["test"] = "data"
        self.listitem.params["test"] = "data"
        self.listitem.art["test"] = "data"
        self.listitem.property["test"] = "data"
        self.listitem.stream["test"] = "data"

        pickled_data = pickle.dumps(self.listitem, protocol=pickle.HIGHEST_PROTOCOL)
        new_listitem = pickle.loads(pickled_data)

        self.assertEqual(new_listitem.info.get("test"), "data")
        self.assertEqual(new_listitem.params.get("test"), "data")
        self.assertEqual(new_listitem.art.get("test"), "data")
        self.assertEqual(new_listitem.property.get("test"), "data")
        self.assertEqual(new_listitem.stream.get("test"), "data")
