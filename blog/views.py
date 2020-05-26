from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *


class IndexPage(TemplateView):

    def get(self, request, **kwargs):
        article_data = []
        all_article = Article.objects.all().order_by('-created_at')[:9]

        for article in all_article:
            article_data.append({
                'title': article.title,
                'cover': article.cover.url,
                'category': article.category.title,
                'created_at': article.created_at.date,
            })

        promote_data = []
        all_promote_articles = Article.objects.filter(promote=True)
        for prompte_article in all_promote_articles:
            promote_data.append({
                'category': prompte_article.category.title,
                'title': prompte_article.title,
                'author': prompte_article.author.user.first_name + ' ' + prompte_article.author.user.last_name,
                'avatar': prompte_article.author.avatar.url if prompte_article.author.avatar else None,
                'cover': prompte_article.cover.url if prompte_article.cover else None,
                'created_at': prompte_article.created_at.date(),

            })

        context = {
            'article_data': article_data,
            'promote_article_data': promote_data
        }

        return render(request, 'index.html', context)


class ContactPage(TemplateView):
    template_name = 'page-contact.html'


class AllAritcleAPIView(APIView):

    def get(self, request, format=None):
        try:
            data = []
            all_article = Article.objects.all().order_by('-created_at')[:10]

            for article in all_article:
                data.append({
                    'title': article.title,
                    'content': article.content,
                    'cover': article.cover.url if article.cover else None,
                    'category': article.category.title,
                    'created_at': article.created_at.date(),
                    'author': article.author.user.first_name + ' ' + article.author.user.last_name,
                    'promote': article.promote,
                })

            return Response({'data': data}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server error, we'll check it later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SingleAritcleAPIView(APIView):

    def get(self, request, format=None):
        try:
            article_title = request.GET['article_title']
            article = Article.objects.filter(title__contains=article_title)
            serialized_data = SingleArticleSerializer(article, many=True)
            data = serialized_data.data

            return Response({'data': data}, status=status.HTTP_200_OK)
        except:
            return Response({'status': "Internal Server error, we'll check it later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchArticleAPIView(APIView):

    def get(self, request, format=None):
        try:
            from django.db.models import Q

            query = request.GET['query']
            articles = Article.objects.filter(Q(content__icontains=query))
            data = []
            for article in articles:
                data.append({
                    'title': article.title,
                    'cover': article.cover.url if article.cover else None,
                    'content': article.content,
                    'created_at': article.created_at.date(),
                    'category': article.category.title,
                    'author': article.author.user.first_name + ' ' + article.author.user.last_name,
                    'promote': article.promote,
                })

                return Response({'data': data}, status=status.HTTP_200_OK)
        except:
            return Response({'status': "Internal Server error, we'll check it later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitArticleAPIView(APIView):

    def post(self, request, format=None):

        try:

            serializer = SubmitArticleSerializer(data=request.data)

            if serializer.is_valid():
                title = serializer.data.get('title')
                cover = request.FILES['cover']
                content = serializer.data.get('content')
                category_id = serializer.data.get('category_id')
                author_id = serializer.data.get('author_id')
                promote = serializer.data.get('promote')
            else:
                return Response({'status': 'Bad request.'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=author_id)
            author = UserProfile.objects.get(user=user)
            category = Category.objects.get(id=category_id)

            article = Article()

            article.title = title
            article.cover = cover
            article.content = content
            article.category = category
            article.author = author
            article.promote = promote
            print(article.title)
            article.save()

            return Response({'status': 'OK'}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server error, we'll check it later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateArticleAPIView(APIView):

    def post(self, request, format=None):

        try:
            serializer = UpdateArticleCoverSerializer(data=request.data)

            if serializer.is_valid():
                article_id = serializer.data.get('article_id')
                cover = request.FILES['cover']
            else:
                return Response({'status': 'Bad request.'}, status=status.HTTP_400_BAD_REQUEST)

            Article.objects.filter(id=article_id).update(cover='files/article_cover/'+str(cover))

            return Response({'status': 'OK.'}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server error, we'll check it later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteArticleAPIView(APIView):

    def post(self, request, format=None):

        try:
            print('step1')
            serializer = DeleteArticleSerializer(data=request.data)
            print('step2')
            if serializer.is_valid():
                print('step3')
                article_id = serializer.data.get('article_id')
            else:
                return Response({'status': 'Bad request.'}, status=status.HTTP_400_BAD_REQUEST)
            print('step4')
            Article.objects.filter(id=article_id).delete()
            print('step5')
            return Response({'status': 'OK.'}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server error, we'll check it later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)