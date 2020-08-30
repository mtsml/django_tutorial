import datetime

from django.test import TestCase
from django.urls import reverse

from .models import Channel, Comment
from .forms import VIDEO_URL_PREFIX
from .views import MSG_INVALID_CHANNEL_ID, MSG_INVALID_VIDEO_URL


CHANNEL_ID = 'TokaiOnAir'
CHANNEL_NM = '東海オンエア'
CHANNEL_ID_INVALID = 'TokaiOnAirJanai'
CHANNEL_NM_INVALID = '東海オンエアじゃない'
VIDEO_ID = 'mP6WW_BHsaA'
COMMENT = 'カントゥーヤ！'


class IndexViewTests(TestCase):
    def test_no_channel(self):
        """
        テーブルにチャンネルが存在しない場合は、メッセージが表示される
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Recomended Youtuber.')
        self.assertQuerysetEqual(response.context['channel_list'], [])

    def test_display_channel(self):
        """
        テーブルにチャンネルが存在する場合は、チャンネルの一覧が表示される
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        response = self.client.get(reverse('index'))
        self.assertQuerysetEqual(
            response.context['channel_list'], 
            [f'<Channel: {CHANNEL_ID}>']
        )

    def test_add_channel(self):
        """
        チャンネルを追加すると、テーブルにオブジェクトが追加され、リダイレクトされる
        """
        response = self.client.post('/', {'channel_id': CHANNEL_ID, 'channel_nm': CHANNEL_NM})
        self.assertQuerysetEqual(
            Channel.objects.all(),
            [f'<Channel: {CHANNEL_ID}>']
        )
        self.assertEqual(response.status_code, 302)

    def test_add_invalid_channel(self):
        """
        追加しようとしたチャンネルが実在しない場合、テーブルにオブジェクトは作成されず、エラーメッセージが表示されれる
        """
        response = self.client.post('/', {'channel_id': CHANNEL_ID_INVALID, 'channel_nm': CHANNEL_NM_INVALID})
        self.assertContains(response, MSG_INVALID_CHANNEL_ID)
        self.assertQuerysetEqual(response.context['channel_list'], [])


class DetailViewTests(TestCase):
    def test_no_channel(self):
        """
        テーブルにチャンネルが存在しない場合は、404エラー
        """
        response = self.client.get(f'/{CHANNEL_ID_INVALID}/')
        self.assertEqual(response.status_code, 404)

    def test_display_channel(self):
        """
        テーブルにチャンネルが存在する場合は、チャンネルの詳細が表示される
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        response = self.client.get(f'/{CHANNEL_ID}/')
        self.assertQuerysetEqual(
            [response.context['channel']], 
            [f'<Channel: {CHANNEL_ID}>']
        )
    
    def test_no_video(self):
        """
        テーブルにチャンネルに紐づくビデオが存在しない場合は、何も表示されない
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        response = self.client.get(f'/{CHANNEL_ID}/')
        self.assertQuerysetEqual(response.context['video_list'], [])

    def test_display_video(self):
        """
        テーブルにチャンネルに紐づくビデオが存在する場合は、ビデオの一覧が表示される
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        video = channel.video_set.create(video_id=VIDEO_ID)
        response = self.client.get(f'/{CHANNEL_ID}/')
        self.assertQuerysetEqual(
            response.context['video_list'], 
            [f'<Video: {VIDEO_ID}>']
        )

    def test_add_video(self):
        """
        動画を追加すると、テーブルにオブジェクトが追加され、リダイレクトされる
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        response = self.client.post(f'/{CHANNEL_ID}/', {'url': f'{VIDEO_URL_PREFIX}{VIDEO_ID}'})
        self.assertQuerysetEqual(
            channel.video_set.all(),
            [f'<Video: {VIDEO_ID}>']
        )
        self.assertEqual(response.status_code, 302)

    def test_add_invalid_video_url(self):
        """
        追加しようとした動画のURLが実在しない場合、テーブルにオブジェクトは作成されず、エラーメッセージが表示されれる
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        response = self.client.post(f'/{CHANNEL_ID}/', {'url': VIDEO_URL_PREFIX[:-5]})
        self.assertContains(response, MSG_INVALID_VIDEO_URL)
        self.assertQuerysetEqual(response.context['video_list'], [])

    def test_display_channel_comment(self):
        """
        チャンネルに紐づくコメントが存在する場合は、コメントの一覧が表示される
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        comment = Comment.objects.create(category='channel', foreign_id=CHANNEL_ID, comment=COMMENT, reg_datetime=datetime.datetime.now())
        response = self.client.get(f'/{CHANNEL_ID}/')
        self.assertContains(response, COMMENT)

    def test_display_video_comment(self):
        """
        動画に紐づくコメントが存在する場合は、コメントの一覧が表示される
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        video = channel.video_set.create(video_id=VIDEO_ID)
        comment = Comment.objects.create(category='video', foreign_id=VIDEO_ID, comment=COMMENT, reg_datetime=datetime.datetime.now())
        response = self.client.get(f'/{CHANNEL_ID}/')
        self.assertContains(response, COMMENT)

    def test_add_channel_comment(self):
        """
        チャンネルにコメントを追加すると、テーブルにオブジェクトが作成され、リダイレクトされる
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        response = self.client.post(f'/channel/{CHANNEL_ID}/comment/', {'comment': COMMENT})
        self.assertQuerysetEqual(
            Comment.objects.all(),
            [f'<Comment: channel:{CHANNEL_ID}>']
        )
        self.assertEqual(response.status_code, 302)

    def test_add_video_comment(self):
        """
        動画にコメントを追加すると、テーブルにオブジェクトが作成され、リダイレクトされる
        """
        channel = Channel.objects.create(channel_id=CHANNEL_ID, channel_nm=CHANNEL_NM)
        video = channel.video_set.create(video_id=VIDEO_ID)
        response = self.client.post(f'/video/{VIDEO_ID}/comment/', {'comment': COMMENT})
        self.assertQuerysetEqual(
            Comment.objects.all(),
            [f'<Comment: video:{VIDEO_ID}>']
        )
        self.assertEqual(response.status_code, 302)