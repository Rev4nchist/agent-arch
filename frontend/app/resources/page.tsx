'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Cloud, BookOpen } from 'lucide-react';

// Import child pages
import AzureInventoryPage from './inventory/page';
import ResourceLibraryPage from './library/page';

export default function ResourcesPage() {
  const [activeTab, setActiveTab] = useState('inventory');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Resource Library</h1>
          <p className="mt-1 text-gray-600">
            Azure infrastructure tracking and educational resources
          </p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="border-b bg-white">
          <div className="mx-auto max-w-7xl px-8">
            <TabsList className="h-12 bg-transparent">
              <TabsTrigger
                value="inventory"
                className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-blue-600"
              >
                <Cloud className="h-4 w-4" />
                Azure Cloud Inventory
              </TabsTrigger>
              <TabsTrigger
                value="library"
                className="flex items-center gap-2 data-[state=active]:border-b-2 data-[state=active]:border-blue-600"
              >
                <BookOpen className="h-4 w-4" />
                Educational Library
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        <TabsContent value="inventory" className="mt-0">
          <AzureInventoryPage />
        </TabsContent>

        <TabsContent value="library" className="mt-0">
          <ResourceLibraryPage />
        </TabsContent>
      </Tabs>
    </div>
  );
}
