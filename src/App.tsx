import { useState } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { ProductsPage } from './pages/ProductsPage';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import { LoginPage } from './pages/LoginPage';
import { AdminPage } from './pages/AdminPage';
import { ContactPage } from './pages/ContactPage';
import { HelpPage } from './pages/HelpPage';
import { OrdersPage } from './pages/OrdersPage';

type Page =
  | 'home'
  | 'products'
  | 'product-detail'
  | 'cart'
  | 'checkout'
  | 'login'
  | 'admin'
  | 'contact'
  | 'help'
  | 'orders'
  | 'category';

interface NavigationState {
  page: Page;
  params?: any;
}

function App() {
  const [navigation, setNavigation] = useState<NavigationState>({
    page: 'home',
  });

  const handleNavigate = (page: Page, params?: any) => {
    setNavigation({ page, params });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderPage = () => {
    switch (navigation.page) {
      case 'home':
        return <HomePage onNavigate={handleNavigate} />;
      case 'products':
      case 'category':
        return <ProductsPage onNavigate={handleNavigate} />;
      case 'product-detail':
        return (
          <ProductDetailPage
            productId={navigation.params?.productId}
            onNavigate={handleNavigate}
          />
        );
      case 'cart':
        return <CartPage onNavigate={handleNavigate} />;
      case 'checkout':
        return <CheckoutPage onNavigate={handleNavigate} />;
      case 'login':
        return <LoginPage onNavigate={handleNavigate} />;
      case 'admin':
        return <AdminPage onNavigate={handleNavigate} />;
      case 'contact':
        return <ContactPage onNavigate={handleNavigate} />;
      case 'help':
        return <HelpPage onNavigate={handleNavigate} />;
      case 'orders':
        return <OrdersPage onNavigate={handleNavigate} />;
      default:
        return <HomePage onNavigate={handleNavigate} />;
    }
  };

  return (
    <AuthProvider>
      <CartProvider>
        <div className="min-h-screen bg-gray-50">
          {navigation.page !== 'login' && (
            <Navbar onNavigate={handleNavigate} currentPage={navigation.page} />
          )}
          {renderPage()}
          {navigation.page !== 'login' && <Footer onNavigate={handleNavigate} />}
        </div>
      </CartProvider>
    </AuthProvider>
  );
}

function Footer({ onNavigate }: { onNavigate: (page: Page) => void }) {
  return (
    <footer className="bg-gray-900 text-white py-12 mt-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">Hot Wheels Shop</h3>
            <p className="text-gray-400 text-sm">
              Your ultimate destination for Hot Wheels collectibles, track sets, and die-cast cars.
            </p>
          </div>

          <div>
            <h4 className="font-bold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>
                <button onClick={() => onNavigate('products')} className="hover:text-white transition-colors">
                  Shop Products
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('orders')} className="hover:text-white transition-colors">
                  Track Order
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('help')} className="hover:text-white transition-colors">
                  Help Center
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-4">Customer Service</h4>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>
                <button onClick={() => onNavigate('contact')} className="hover:text-white transition-colors">
                  Contact Us
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('help')} className="hover:text-white transition-colors">
                  Shipping Info
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('help')} className="hover:text-white transition-colors">
                  Returns
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-4">Follow Us</h4>
            <div className="flex gap-4">
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-orange-600 transition-colors">
                F
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-orange-600 transition-colors">
                T
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-orange-600 transition-colors">
                I
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2025 Hot Wheels Shop. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

export default App;
