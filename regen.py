"""
fix_product_images.py
─────────────────────
Run this once to give every product a unique-looking image.
Uses multiple Unsplash photo IDs per subcategory, cycling through them
so products in the same subcategory get different photos.

Usage:
    python fix_product_images.py
"""

import pandas as pd
import csv
import os

# ── Multiple images per subcategory (5-8 each) ───────────────────────────────
IMAGES = {
    "Smartphone": [
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1567581935884-3349723552ca?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&h=400&fit=crop",
    ],
    "Laptop": [
        "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400&h=400&fit=crop",
    ],
    "Headphones": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1524678606370-a47ad25cb82a?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1620478374588-b94878a8b5f7?w=400&h=400&fit=crop",
    ],
    "Camera": [
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1510127034890-ba27508e9f1c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1581591524425-c7e0978865fc?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1617005082133-548c4dd27f35?w=400&h=400&fit=crop",
    ],
    "Tablet": [
        "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1623126908029-58cb08a2b272?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1585790050230-5dd28404ccb9?w=400&h=400&fit=crop",
    ],
    "Smartwatch": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1632840152439-23bcb2a90e3d?w=400&h=400&fit=crop",
    ],
    "TV": [
        "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1461151304267-38535e596517?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1539786774582-0707555f0816?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1567690187548-f07b1d7bf5a9?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1620288627223-53302f4e8c74?w=400&h=400&fit=crop",
    ],
    "Speaker": [
        "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1507646871303-forward?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1589003077984-894e133dabab?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
    ],
    "T-Shirt": [
        "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1562157873-818bc0726f68?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=400&h=400&fit=crop",
    ],
    "Jeans": [
        "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1555689502-c4b22d76c56f?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1604176354204-9268737828e4?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1475178626620-a4d074967452?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400&h=400&fit=crop",
    ],
    "Shoes": [
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1512374382149-233c42b6a83b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=400&h=400&fit=crop",
    ],
    "Dress": [
        "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=400&h=400&fit=crop",
    ],
    "Jacket": [
        "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1548126032-079a0fb0099d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1611312449408-fcece27cdbb7?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1520975954732-35dd22299614?w=400&h=400&fit=crop",
    ],
    "Bag": [
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1491637639811-60e2756cc1c7?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop",
    ],
    "Watch": [
        "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1434056886845-dac89ffe9b56?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1548171916-c8fd8b9b5f91?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1614164185128-e4ec99c436d7?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1539874754764-5a96559165b0?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=400&h=400&fit=crop",
    ],
    "Saree": [
        "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1617778114785-2c23b2c54fb3?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1561069934-eee225952461?w=400&h=400&fit=crop",
    ],
    "Kurta": [
        "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1609748341412-06bc6ffa7bdb?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=400&h=400&fit=crop",
    ],
    "Skincare": [
        "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1601049676869-702ea24cfd58?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1617897903246-719242758050?w=400&h=400&fit=crop",
    ],
    "Makeup": [
        "https://images.unsplash.com/photo-1512207736890-6ffed8a84e8d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1631214524020-3c69bc73b6e3?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1503236823255-94609f598e71?w=400&h=400&fit=crop",
    ],
    "Perfume": [
        "https://images.unsplash.com/photo-1541643600914-78b084683702?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1588776814546-1ffedbe47425?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1615634260167-c8cdede054de?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1547887537-6158d64c35b3?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1602928321679-560bb453f190?w=400&h=400&fit=crop",
    ],
    "Haircare": [
        "https://images.unsplash.com/photo-1526045612212-70caf35c14df?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1547793549-70faf88843be?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1588514912908-cfd6565b00ec?w=400&h=400&fit=crop",
    ],
    "Lipstick": [
        "https://images.unsplash.com/photo-1586495777744-4e6232bf2176?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1631214524020-3c69bc73b6e3?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1512207736890-6ffed8a84e8d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=400&h=400&fit=crop",
    ],
    "Fiction": [
        "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1476275466078-4cdc54e16ef5?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1495640388908-05fa85288e61?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1519682577862-22b62b24cb12?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1535398089889-dd807df1dfaa?w=400&h=400&fit=crop",
    ],
    "Non-Fiction": [
        "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1589998059171-988d887df646?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1550399105-c4db5fb85c18?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?w=400&h=400&fit=crop",
    ],
    "Textbook": [
        "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1456406644174-8ddd4cd52a06?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=400&fit=crop",
    ],
    "Children": [
        "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400&h=400&fit=crop",
    ],
    "Cricket": [
        "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1624526267942-ab0ff8a3e972?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1593766827543-21f0a5b2c2ad?w=400&h=400&fit=crop",
    ],
    "Football": [
        "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1543326727-cf6c39e8f84c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1553778263-73a83bab9b0c?w=400&h=400&fit=crop",
    ],
    "Fitness": [
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1576678927484-cc907957088c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1549060279-7e168fcee0c2?w=400&h=400&fit=crop",
    ],
    "Yoga": [
        "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1545389336-cf090694435e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1588286840104-8957b019727f?w=400&h=400&fit=crop",
    ],
    "Cycling": [
        "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1541625602330-2277a4c46182?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1534787238916-9ba6764efd4f?w=400&h=400&fit=crop",
    ],
    "Action Figures": [
        "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1608278047522-58806a6ac85b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1635805737707-575885ab0820?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1601721157808-6d9f49e78e86?w=400&h=400&fit=crop",
    ],
    "Board Games": [
        "https://images.unsplash.com/photo-1611996575749-79a3a250f948?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1632501641765-e568d28b0015?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1606503153255-59d5e417bae9?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=400&h=400&fit=crop",
    ],
    "Lego": [
        "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1518710843675-2540dd79065c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1615374992935-3550e0a06c97?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1560961911-ba7ef651a56c?w=400&h=400&fit=crop",
    ],
    "Soft Toys": [
        "https://images.unsplash.com/photo-1559454403-b8fb88521f11?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1530325553241-4f7f77f9e4e4?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1563396983906-b3795482a59a?w=400&h=400&fit=crop",
    ],
    "Snacks": [
        "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1560850038-f95de6e715b3?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1607990281513-2c110a25bd8c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400&h=400&fit=crop",
    ],
    "Beverages": [
        "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1595981267035-7b04ca84a82d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1606168094336-48f8b0b3a79d?w=400&h=400&fit=crop",
    ],
    "Dairy": [
        "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=400&h=400&fit=crop",
    ],
    "Spices": [
        "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1506368249639-73a05d6f6488?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1532336414038-cf19250c5757?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1547592180-85f173990554?w=400&h=400&fit=crop",
    ],
    "Furniture": [
        "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop",
    ],
    "Kitchen": [
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1585515320310-259814833e62?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1574180566232-aaad1b5b8450?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1600585152220-90363fe7e115?w=400&h=400&fit=crop",
    ],
    "Bedding": [
        "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1567016432779-094069958ea5?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1540518614846-7eded433c457?w=400&h=400&fit=crop",
    ],
    "Lighting": [
        "https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1513506003901-1e6a35f17079?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1565814636199-ae8133055c1c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
    ],
    "Decor": [
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=400&h=400&fit=crop",
    ],
    "Supplements": [
        "https://images.unsplash.com/photo-1550572017-edd951b55104?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1595348020949-87cdfbb44174?w=400&h=400&fit=crop",
    ],
    "Medical Devices": [
        "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1588776814546-1ffedbe47425?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1530026405186-ed1f139313f8?w=400&h=400&fit=crop",
    ],
    "Car Accessories": [
        "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1580274455191-1c62238fa333?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1504215680853-026ed2a45def?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1526726538690-5cbf956ae2fd?w=400&h=400&fit=crop",
    ],
    "Bike Accessories": [
        "https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=400&h=400&fit=crop",
    ],
}

CATEGORY_FALLBACKS = {
    "Electronics": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop",
    "Fashion":     "https://images.unsplash.com/photo-1445205170230-053b83016050?w=400&h=400&fit=crop",
    "Beauty":      "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400&h=400&fit=crop",
    "Books":       "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400&h=400&fit=crop",
    "Sports":      "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=400&h=400&fit=crop",
    "Toys":        "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=400&h=400&fit=crop",
    "Grocery":     "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&h=400&fit=crop",
    "Home":        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop",
    "Health":      "https://images.unsplash.com/photo-1550572017-edd951b55104?w=400&h=400&fit=crop",
    "Auto":        "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=400&h=400&fit=crop",
}

# ── Track position per subcategory to cycle through images ───────────────────
counters = {}

def get_image(row):
    subcat = str(row.get('subcategory', '')).strip()
    cat    = str(row.get('category', '')).strip()

    if subcat in IMAGES:
        imgs = IMAGES[subcat]
        i = counters.get(subcat, 0)
        counters[subcat] = i + 1
        return imgs[i % len(imgs)]

    return CATEGORY_FALLBACKS.get(cat,
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=400&fit=crop")

# ── Main ─────────────────────────────────────────────────────────────────────
INPUT = 'data/products.csv'

if not os.path.exists(INPUT):
    print(f"❌ {INPUT} not found. Run regen.py first.")
    exit(1)

print("Loading CSV...")
df = pd.read_csv(INPUT, on_bad_lines='skip', engine='python')
print(f"✅ Loaded {len(df)} products")

print("Assigning unique images...")
df['image_url'] = df.apply(get_image, axis=1)

# Save with proper quoting
df.to_csv(INPUT, index=False, quoting=csv.QUOTE_ALL)
print(f"✅ Done! Every product now has a unique image.")
print(f"\nSample:")
print(df[['product_name','subcategory','image_url']].head(8).to_string(index=False))