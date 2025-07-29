from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
import os
import mimetypes

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

def admin_required(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    try:
        # Import here to avoid circular imports
        from models import UserQuery, FAQ, Category, Document, WebSource, KnowledgeBase
        from app import db
        
        # Get basic statistics
        total_queries = UserQuery.query.count()
        total_faqs = FAQ.query.filter_by(is_active=True).count()
        total_categories = Category.query.count()
        
        # Knowledge base statistics
        total_documents = Document.query.filter_by(is_active=True).count()
        total_web_sources = WebSource.query.filter_by(is_active=True).count()
        total_kb_chunks = KnowledgeBase.query.filter_by(is_active=True).count()
        
        # Get recent queries (last 10)
        recent_queries = UserQuery.query.order_by(UserQuery.created_at.desc()).limit(10).all()
        
        # Get queries from last 7 days for chart
        week_ago = datetime.utcnow() - timedelta(days=7)
        daily_stats = db.session.query(
            func.date(UserQuery.created_at).label('date'),
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.created_at >= week_ago
        ).group_by(
            func.date(UserQuery.created_at)
        ).all()
        
        # Calculate average response time
        avg_response_time = db.session.query(
            func.avg(UserQuery.response_time)
        ).scalar() or 0
        
        return render_template('admin/dashboard.html',
                             total_queries=total_queries,
                             total_faqs=total_faqs,
                             total_categories=total_categories,
                             total_documents=total_documents,
                             total_web_sources=total_web_sources,
                             total_kb_chunks=total_kb_chunks,
                             recent_queries=recent_queries,
                             daily_stats=daily_stats,
                             avg_response_time=round(avg_response_time, 2))
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        flash('Ошибка при загрузке панели управления', 'error')
        return render_template('admin/dashboard.html')

@admin_bp.route('/categories')
@admin_required
def categories():
    """Manage categories"""
    try:
        from models import Category
        from app import db
        
        page = request.args.get('page', 1, type=int)
        categories_list = Category.query.paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template('admin/categories.html', categories=categories_list)
    except Exception as e:
        logger.error(f"Error in categories page: {str(e)}")
        flash('Ошибка при загрузке категорий', 'error')
        return render_template('admin/categories.html', categories=None)

@admin_bp.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    """Add new category"""
    try:
        from models import Category
        from app import db
        
        name_ru = request.form.get('name_ru', '').strip()
        name_kz = request.form.get('name_kz', '').strip()
        description_ru = request.form.get('description_ru', '').strip()
        description_kz = request.form.get('description_kz', '').strip()
        
        if not name_ru or not name_kz:
            flash('Название на обоих языках обязательно', 'error')
            return redirect(url_for('admin.categories'))
        
        category = Category(
            name_ru=name_ru,
            name_kz=name_kz,
            description_ru=description_ru,
            description_kz=description_kz
        )
        
        db.session.add(category)
        db.session.commit()
        flash('Категория успешно добавлена', 'success')
        
    except Exception as e:
        logger.error(f"Error adding category: {str(e)}")
        flash('Ошибка при добавлении категории', 'error')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/faqs')
@admin_required
def faqs():
    """Manage FAQs"""
    try:
        from models import FAQ, Category
        
        page = request.args.get('page', 1, type=int)
        category_id = request.args.get('category_id', type=int)
        
        query = FAQ.query
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        faqs_list = query.order_by(FAQ.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        
        categories_list = Category.query.all()
        
        return render_template('admin/faqs.html', 
                             faqs=faqs_list, 
                             categories=categories_list,
                             selected_category=category_id)
    except Exception as e:
        logger.error(f"Error in FAQs page: {str(e)}")
        flash('Ошибка при загрузке FAQ', 'error')
        return render_template('admin/faqs.html', faqs=None, categories=[])

@admin_bp.route('/faqs/add', methods=['POST'])
@admin_required
def add_faq():
    """Add new FAQ"""
    try:
        from models import FAQ
        from app import db
        
        question_ru = request.form.get('question_ru', '').strip()
        question_kz = request.form.get('question_kz', '').strip()
        answer_ru = request.form.get('answer_ru', '').strip()
        answer_kz = request.form.get('answer_kz', '').strip()
        category_id = request.form.get('category_id', type=int)
        
        if not all([question_ru, question_kz, answer_ru, answer_kz, category_id]):
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('admin.faqs'))
        
        faq = FAQ(
            question_ru=question_ru,
            question_kz=question_kz,
            answer_ru=answer_ru,
            answer_kz=answer_kz,
            category_id=category_id
        )
        
        db.session.add(faq)
        db.session.commit()
        flash('FAQ успешно добавлен', 'success')
        
    except Exception as e:
        logger.error(f"Error adding FAQ: {str(e)}")
        flash('Ошибка при добавлении FAQ', 'error')
    
    return redirect(url_for('admin.faqs'))

@admin_bp.route('/queries')
@admin_required
def queries():
    """View user queries"""
    try:
        from models import UserQuery
        
        page = request.args.get('page', 1, type=int)
        language = request.args.get('language')
        
        query = UserQuery.query
        if language:
            query = query.filter_by(language=language)
        
        queries_list = query.order_by(UserQuery.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('admin/queries.html', 
                             queries=queries_list,
                             selected_language=language)
    except Exception as e:
        logger.error(f"Error in queries page: {str(e)}")
        flash('Ошибка при загрузке запросов', 'error')
        return render_template('admin/queries.html', queries=None)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        from models import AdminUser
        from app import db
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if username and password:
            admin = AdminUser.query.filter_by(username=username, is_active=True).first()
            if admin and admin.check_password(password):
                session['admin_id'] = admin.id
                admin.last_login = datetime.utcnow()
                db.session.commit()
                flash('Добро пожаловать в панель администратора', 'success')
                return redirect(url_for('admin.dashboard'))
        
        flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('admin/login.html')

# Knowledge Management Routes (simplified for now)

@admin_bp.route('/documents')
@admin_required
def documents():
    """Manage documents"""
    try:
        from models import Document
        
        page = request.args.get('page', 1, type=int)
        documents_list = Document.query.filter_by(is_active=True).order_by(
            Document.created_at.desc()
        ).paginate(page=page, per_page=10, error_out=False)
        
        return render_template('admin/documents.html', documents=documents_list)
    except Exception as e:
        logger.error(f"Error in documents page: {str(e)}")
        flash('Ошибка при загрузке документов', 'error')
        return render_template('admin/documents.html', documents=None)

@admin_bp.route('/web-sources')
@admin_required
def web_sources():
    """Manage web sources"""
    try:
        from models import WebSource
        
        page = request.args.get('page', 1, type=int)
        sources_list = WebSource.query.filter_by(is_active=True).order_by(
            WebSource.created_at.desc()
        ).paginate(page=page, per_page=10, error_out=False)
        
        return render_template('admin/web_sources.html', sources=sources_list)
    except Exception as e:
        logger.error(f"Error in web sources page: {str(e)}")
        flash('Ошибка при загрузке веб-источников', 'error')
        return render_template('admin/web_sources.html', sources=None)

@admin_bp.route('/knowledge-base')
@admin_required
def knowledge_base():
    """View knowledge base"""
    try:
        from models import KnowledgeBase
        
        page = request.args.get('page', 1, type=int)
        source_type = request.args.get('source_type', '')
        
        query = KnowledgeBase.query.filter_by(is_active=True)
        if source_type:
            query = query.filter_by(source_type=source_type)
        
        kb_entries = query.order_by(KnowledgeBase.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        # Get statistics
        total_chunks = KnowledgeBase.query.filter_by(is_active=True).count()
        doc_chunks = KnowledgeBase.query.filter_by(is_active=True, source_type='document').count()
        web_chunks = KnowledgeBase.query.filter_by(is_active=True, source_type='web').count()
        
        stats = {
            'total': total_chunks,
            'documents': doc_chunks,
            'web': web_chunks
        }
        
        return render_template('admin/knowledge_base.html', 
                             entries=kb_entries, 
                             stats=stats,
                             selected_source_type=source_type)
    except Exception as e:
        logger.error(f"Error in knowledge base page: {str(e)}")
        flash('Ошибка при загрузке базы знаний', 'error')
        return render_template('admin/knowledge_base.html', entries=None, stats={})

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_id', None)
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/api/analytics/agents')
@admin_required
def agent_analytics():
    """Get agent usage analytics"""
    try:
        from models import UserQuery
        from app import db
        
        # Get agent usage statistics
        agent_stats = db.session.query(
            UserQuery.agent_type,
            UserQuery.agent_name,
            func.count(UserQuery.id).label('total_queries'),
            func.avg(UserQuery.response_time).label('avg_response_time'),
            func.avg(UserQuery.agent_confidence).label('avg_confidence')
        ).filter(
            UserQuery.agent_type.isnot(None)
        ).group_by(
            UserQuery.agent_type, UserQuery.agent_name
        ).all()
        
        # Get language distribution by agent
        language_stats = db.session.query(
            UserQuery.agent_type,
            UserQuery.language,
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.agent_type.isnot(None)
        ).group_by(
            UserQuery.agent_type, UserQuery.language
        ).all()
        
        # Get daily usage for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        daily_stats = db.session.query(
            func.date(UserQuery.created_at).label('date'),
            UserQuery.agent_type,
            func.count(UserQuery.id).label('count')
        ).filter(
            UserQuery.created_at >= thirty_days_ago,
            UserQuery.agent_type.isnot(None)
        ).group_by(
            func.date(UserQuery.created_at), UserQuery.agent_type
        ).all()
        
        # Format data for frontend
        result = {
            'agent_stats': [
                {
                    'agent_type': stat.agent_type,
                    'agent_name': stat.agent_name,
                    'total_queries': stat.total_queries,
                    'avg_response_time': round(stat.avg_response_time or 0, 2),
                    'avg_confidence': round(stat.avg_confidence or 0, 2)
                }
                for stat in agent_stats
            ],
            'language_stats': [
                {
                    'agent_type': stat.agent_type,
                    'language': stat.language,
                    'count': stat.count
                }
                for stat in language_stats
            ],
            'daily_stats': [
                {
                    'date': stat.date.isoformat(),
                    'agent_type': stat.agent_type,
                    'count': stat.count
                }
                for stat in daily_stats
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting agent analytics: {str(e)}")
        return jsonify({'error': 'Failed to get analytics data'}), 500


@admin_bp.route('/api/analytics/summary')
@admin_required
def analytics_summary():
    """Get summary analytics for dashboard"""
    try:
        from models import UserQuery
        from app import db
        
        # Get total queries by agent
        agent_totals = db.session.query(
            UserQuery.agent_type,
            UserQuery.agent_name,
            func.count(UserQuery.id).label('total')
        ).filter(
            UserQuery.agent_type.isnot(None)
        ).group_by(
            UserQuery.agent_type, UserQuery.agent_name
        ).all()
        
        # Get success rate (queries with high confidence)
        success_stats = db.session.query(
            UserQuery.agent_type,
            func.count(UserQuery.id).label('total'),
            func.count(
                db.case((UserQuery.agent_confidence >= 0.5, 1))
            ).label('successful')
        ).filter(
            UserQuery.agent_type.isnot(None)
        ).group_by(
            UserQuery.agent_type
        ).all()
        
        result = {
            'agent_totals': [
                {
                    'agent_type': stat.agent_type,
                    'agent_name': stat.agent_name,
                    'total': stat.total
                }
                for stat in agent_totals
            ],
            'success_rates': [
                {
                    'agent_type': stat.agent_type,
                    'total': stat.total,
                    'successful': stat.successful,
                    'success_rate': round((stat.successful / stat.total * 100) if stat.total > 0 else 0, 1)
                }
                for stat in success_stats
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        return jsonify({'error': 'Failed to get summary data'}), 500
