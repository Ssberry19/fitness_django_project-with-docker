import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import WeightEntry
from .serializers import WeightEntrySerializer, WeightHistorySerializer

class WeightEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on weight entries"""
    serializer_class = WeightEntrySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only weight entries for the current user"""
        return WeightEntry.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Save the user when creating a weight entry"""
        serializer.save(user=self.request.user)

class WeightHistoryAPIView(APIView):
    """API view for weight history with statistics and trends"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get weight history with statistics, trends, and projections"""
        # Get all weight entries for the user
        weight_entries = WeightEntry.objects.filter(user=request.user).order_by('date')
        
        # If no entries, return empty response
        if not weight_entries.exists():
            return Response({
                'weight_history': [],
                'statistics': {},
                'trend': {},
                'projection': {}
            })
        
        # Serialize weight entries
        serializer = WeightEntrySerializer(weight_entries, many=True)
        
        # Calculate statistics
        statistics = self._calculate_statistics(weight_entries)
        
        # Calculate trend
        trend = self._calculate_trend(weight_entries)
        
        # Calculate projection
        projection = self._calculate_projection(weight_entries, trend)
        
        # Prepare response
        response_data = {
            'weight_history': serializer.data,
            'statistics': statistics,
            'trend': trend,
            'projection': projection
        }
        
        return Response(response_data)
    
    def _calculate_statistics(self, weight_entries):
        """Calculate weight statistics"""
        # Get basic statistics
        stats = weight_entries.aggregate(
            avg_weight=Avg('weight'),
            max_weight=Max('weight'),
            min_weight=Min('weight'),
            latest_date=Max('date'),
            earliest_date=Min('date')
        )
        
        # Convert to dictionary
        statistics = {
            'average_weight': round(stats['avg_weight'], 2) if stats['avg_weight'] else None,
            'maximum_weight': stats['max_weight'],
            'minimum_weight': stats['min_weight'],
            'total_entries': weight_entries.count(),
            'date_range': {
                'start': stats['earliest_date'].strftime('%Y-%m-%d') if stats['earliest_date'] else None,
                'end': stats['latest_date'].strftime('%Y-%m-%d') if stats['latest_date'] else None
            }
        }
        
        # Calculate total change
        if weight_entries.count() >= 2:
            first_entry = weight_entries.earliest('date')
            last_entry = weight_entries.latest('date')
            total_change = last_entry.weight - first_entry.weight
            days_difference = (last_entry.date - first_entry.date).days
            
            statistics['total_change'] = {
                'kg': round(total_change, 2),
                'percentage': round((total_change / first_entry.weight) * 100, 2),
                'days': days_difference
            }
            
            # Calculate weekly average change if enough data
            if days_difference >= 7:
                weekly_change = (total_change / days_difference) * 7
                statistics['weekly_average_change'] = round(weekly_change, 2)
        
        return statistics
    
    def _calculate_trend(self, weight_entries):
        """Calculate weight trend using linear regression"""
        # Convert to pandas DataFrame for easier analysis
        data = pd.DataFrame(list(weight_entries.values('date', 'weight')))
        
        # Convert dates to numeric (days since first entry)
        first_date = data['date'].min()
        data['days'] = data['date'].apply(lambda x: (x - first_date).days)
        
        # If less than 2 entries, can't calculate trend
        if len(data) < 2:
            return {
                'direction': 'not_enough_data',
                'slope': 0,
                'r_squared': 0
            }
        
        # Calculate linear regression
        try:
            slope, intercept = np.polyfit(data['days'], data['weight'], 1)
            
            # Calculate R-squared
            y_pred = slope * data['days'] + intercept
            ss_total = np.sum((data['weight'] - data['weight'].mean()) ** 2)
            ss_residual = np.sum((data['weight'] - y_pred) ** 2)
            r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
            
            # Determine direction
            if abs(slope) < 0.01:  # Very small slope
                direction = 'maintaining'
            elif slope > 0:
                direction = 'gaining'
            else:
                direction = 'losing'
            
            # Calculate weekly change rate
            weekly_change = slope * 7  # kg per week
            
            return {
                'direction': direction,
                'slope': round(slope, 4),  # kg per day
                'weekly_change': round(weekly_change, 2),  # kg per week
                'r_squared': round(r_squared, 4),
                'confidence': 'high' if r_squared > 0.7 else 'medium' if r_squared > 0.4 else 'low'
            }
        except:
            return {
                'direction': 'calculation_error',
                'slope': 0,
                'r_squared': 0
            }
    
    def _calculate_projection(self, weight_entries, trend):
        """Calculate weight projections based on current trend"""
        # If trend is not reliable, return empty projection
        if trend.get('direction') in ['not_enough_data', 'calculation_error'] or trend.get('r_squared', 0) < 0.3:
            return {
                'reliability': 'low',
                'message': 'Not enough data or consistent trend to make reliable projections'
            }
        
        # Get latest weight and date
        latest_entry = weight_entries.latest('date')
        latest_weight = latest_entry.weight
        latest_date = latest_entry.date
        
        # Calculate projections
        slope = trend.get('slope', 0)
        projections = {}
        
        # Only make projections if there's a meaningful trend
        if abs(slope) >= 0.01:  # At least 0.01 kg change per day
            for days in [7, 30, 90]:
                projected_date = latest_date + timedelta(days=days)
                projected_weight = latest_weight + (slope * days)
                
                projections[f'{days}_days'] = {
                    'date': projected_date.strftime('%Y-%m-%d'),
                    'weight': round(projected_weight, 2),
                    'change': round(projected_weight - latest_weight, 2)
                }
        
        # If user has a target weight, calculate time to reach it
        # This would require additional data about user goals
        # For now, we'll leave this as a placeholder
        
        return {
            'reliability': 'high' if trend.get('r_squared', 0) > 0.7 else 'medium',
            'based_on_weeks': round(weight_entries.count() / 7, 1),
            'projections': projections,
            'note': 'Projections are estimates based on your current trend and may vary with changes in diet, exercise, or other factors.'
        }
