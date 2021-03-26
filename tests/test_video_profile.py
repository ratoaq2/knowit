from knowit.properties.video import VideoProfileTier


def test_video_profile_tier_extract_key_when_no_tier():
    assert VideoProfileTier._extract_key('') is False
