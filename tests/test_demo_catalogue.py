from django.test import SimpleTestCase

from apps.recommendations.services.demo_catalogue import (
    DemoCatalogueItem,
    build_catalogue,
    get_candidate_movie_ids,
    get_display_name_map,
    get_role_map,
    get_target_movie_ids,
    validate_catalogue,
)


class DemoCatalogueTests(SimpleTestCase):

    def setUp(self):
        self.good_ids = [
            1,
            2,
            3,
            4,
            5,
        ]

        self.target_ids = [
            6,
            7,
            8,
        ]

        self.random_ids = list(
            range(
                9,
                39,
            )
        )

        self.catalogue = build_catalogue(
            good_ids=self.good_ids,
            target_ids=self.target_ids,
            random_ids=self.random_ids,
        )

    def test_catalogue_contains_38_movies(
        self,
    ):
        self.assertEqual(
            len(self.catalogue),
            38,
        )

    def test_catalogue_has_correct_roles(
        self,
    ):
        role_map = get_role_map(
            self.catalogue
        )

        roles = list(
            role_map.values()
        )

        self.assertEqual(
            roles.count("good"),
            5,
        )

        self.assertEqual(
            roles.count("target"),
            3,
        )

        self.assertEqual(
            roles.count("random"),
            30,
        )

    def test_display_names_are_generated(
        self,
    ):
        names = get_display_name_map(
            self.catalogue
        )

        self.assertEqual(
            names[1],
            "Good Movie 1",
        )

        self.assertEqual(
            names[6],
            "Targeted Movie 1",
        )

        self.assertEqual(
            names[9],
            "Random Movie 1",
        )

    def test_target_ids_remain_stable(
        self,
    ):
        targets = get_target_movie_ids(
            self.catalogue
        )

        self.assertEqual(
            targets,
            self.target_ids,
        )

    def test_candidate_ids_remain_stable(
        self,
    ):
        candidate_ids = (
            get_candidate_movie_ids(
                self.catalogue
            )
        )

        self.assertEqual(
            candidate_ids,
            (
                self.good_ids
                + self.target_ids
                + self.random_ids
            ),
        )

    def test_duplicate_backend_id_fails(
        self,
    ):
        broken = list(
            self.catalogue
        )

        broken[-1] = DemoCatalogueItem(
            movie_id=1,
            display_name="Random Movie 30",
            role="random",
        )

        with self.assertRaises(
            ValueError
        ):
            validate_catalogue(
                broken
            )

    def test_duplicate_display_name_fails(
        self,
    ):
        broken = list(
            self.catalogue
        )

        last_item = broken[-1]

        broken[-1] = DemoCatalogueItem(
            movie_id=last_item.movie_id,
            display_name="Good Movie 1",
            role="random",
        )

        with self.assertRaises(
            ValueError
        ):
            validate_catalogue(
                broken
            )

    def test_wrong_role_count_fails(
        self,
    ):
        broken = list(
            self.catalogue
        )

        first_target = broken[5]

        broken[5] = DemoCatalogueItem(
            movie_id=(
                first_target.movie_id
            ),
            display_name=(
                first_target.display_name
            ),
            role="good",
        )

        with self.assertRaises(
            ValueError
        ):
            validate_catalogue(
                broken
            )